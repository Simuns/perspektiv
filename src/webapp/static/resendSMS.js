const form = document.querySelector('form[name="resend-SMS"]');

form.addEventListener('submit', (event) => {
  event.preventDefault();


  const sessionIdInput = document.querySelector('input[name="session_id"]');
  const sessionId = sessionIdInput.value;

  // Make a POST request to /send_sms with the phone number and session ID as the request data
  fetch('/send_sms', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ session_id: sessionId })
  });
});