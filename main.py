import os
import uuid
import whisper
import google.generativeai as genai
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from typing import List, Dict
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI
app = FastAPI(title="AI Banking Assistant", description="AI-powered Voice and Spending Analysis")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Database Setup (PostgreSQL/MySQL/SQLite Ready)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./banking.db")  # Default to SQLite

# Validate and parse the DATABASE_URL
def validate_database_url(database_url: str) -> str:
    try:
        parsed_url = urlparse(database_url)
        if parsed_url.scheme == "sqlite":
            return database_url  # No port needed for SQLite
        if parsed_url.port is None:
            raise ValueError("Port is missing in the DATABASE_URL.")
        return database_url
    except Exception as e:
        raise ValueError(f"Invalid DATABASE_URL: {database_url}. Error: {str(e)}")

# Ensure DATABASE_URL is valid
try:
    DATABASE_URL = validate_database_url(DATABASE_URL)
except ValueError as e:
    raise RuntimeError(f"Configuration Error: {e}")

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="transactions")

# Create tables
Base.metadata.create_all(bind=engine)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ User Authentication
@app.post("/register/")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = bcrypt.hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "user_id": user.id}

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": user.username, "exp": datetime.utcnow() + timedelta(days=1)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# ✅ Get Current User
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Voice-to-Text (Whisper)
@app.post("/voice-to-text/")
async def voice_to_text(file: UploadFile = File(...)):
    model = whisper.load_model("base")  # Load model on demand
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")
    temp_filename = f"temp_{uuid.uuid4().hex}.wav"
    try:
        with open(temp_filename, "wb") as f:
            f.write(file.file.read())
        result = model.transcribe(temp_filename)
        return {"text": result["text"]}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# ✅ Spending Analysis (Gemini AI)
@app.post("/analyze-spending/")
async def analyze_spending(transactions: List[Dict], user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not transactions:
        raise HTTPException(status_code=400, detail="Transaction list is empty.")
    try:
        transaction_text = "\n".join([f"{t['description']} - ₹{t['amount']} ({t['category']})" for t in transactions])
        prompt = f"Analyze these banking transactions and provide financial insights:\n{transaction_text}"
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transactions: {str(e)}")

# ✅ Get User Transactions
@app.get("/user-transactions/")
async def get_user_transactions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found.")
    return {
        "transactions": [
            {"id": t.id, "description": t.description, "amount": t.amount, "category": t.category}
            for t in transactions
        ]
    }

# ✅ API Status
@app.get("/")
async def root():
    return {"message": "AI Banking Assistant Backend is Running!"}
