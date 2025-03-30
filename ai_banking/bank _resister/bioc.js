// Simulate the biometric authentication process
function startAuthentication() {
    alert("Biometric authentication started! (This is a simulation, not actual biometric data).");
  
    // Simulating fingerprint scan process
    setTimeout(function() {
      alert("Authentication successful! You are now logged in.");
    }, 3000); // 3 seconds delay to simulate fingerprint scanning
  }
  
  function cancelAuthentication() {
    alert("Authentication canceled.");
  }
  
  // Simulate Google Login button click (for demo purposes)
  document.getElementById('googleLogin').addEventListener('click', function() {
    alert("Google Login clicked! This can be integrated with Google's OAuth API.");
  });
  