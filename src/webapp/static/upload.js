document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('upload-form');
  const message = document.getElementById('message');

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const file = event.target.elements.picture.files[0];
    const session_id = form.querySelector('input[name="session_id"]').value;
    const formData = new FormData();
    formData.append('picture', file);
    formData.append('session_id', session_id);
    fetch('/upload', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      message.textContent = 'File uploaded.';
    })
    .catch(error => console.error(error));
  });
});
  