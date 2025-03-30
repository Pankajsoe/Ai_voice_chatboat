document.addEventListener('DOMContentLoaded', function () {
    const bankForm = document.getElementById('bankForm');
    const responseMessage = document.getElementById('responseMessage');
  
    bankForm.addEventListener('submit', function (e) {
      e.preventDefault(); // Prevent form submission
  
      const fullName = document.getElementById('fullName').value.trim();
      const accountNumber = document.getElementById('accountNumber').value.trim();
      const accountType = document.getElementById('accountType').value;
      const amount = document.getElementById('amount').value;
      const dob = document.getElementById('dob').value;
      const email = document.getElementById('email').value.trim();
      const phone = document.getElementById('phone').value.trim();
      const address = document.getElementById('address').value.trim();
      const terms = document.getElementById('terms').checked;
  
      // Simple client-side validation
      if (!fullName || !accountNumber || !accountType || !amount || !dob || !email || !phone || !address || !terms) {
        responseMessage.style.color = 'red';
        responseMessage.textContent = 'Please fill out all fields and agree to terms.';
        return;
      }
  
      // Simulate successful submission (you can replace this with real server-side logic)
      responseMessage.style.color = 'green';
      responseMessage.textContent = 'Form submitted successfully! Thank you for your submission.';
  
      // Reset the form after submission
      bankForm.reset();
    });
  });
  