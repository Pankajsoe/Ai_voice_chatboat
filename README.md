 AI Banking Assistant

An AI-powered voice banking assistant with multilingual support and spending analysis.

Features

- User Authentication (Register/Login)
- Voice-to-Text (Whisper AI)
- Spending Analysis (Gemini AI)
- Secure Transactions Management

 Tech Stack

- FastAPI
- PostgreSQL
- Whisper AI
- Gemini AI
- JWT Authentication

 Installation

```bash
Clone the repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

Install dependencies
pip install -r requirements.txt

Setup environment variables
cp .env.example .env  # Fill in your details

Run the server
uvicorn main:app --reload
```

Deployment on Render

1. Push code to GitHub.
2. Create a new Web Service on Render.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add environment variables from `.env` file.
6. Deploy and access via Render URL.

 API Endpoints

- `` - Register new user
- `` - Authenticate user
- `` - Convert voice to text
- `` - Get financial insights
- `` - Fetch user transactions

 License

MIT License

