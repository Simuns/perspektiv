postButton.addEventListener('click', (event) => {
if (userContentWritten) {
    
    const textareaElement = document.getElementById('stubbiTextArea');
    const textareaValue = textareaElement.value;

    const data = { text: textareaValue };

    fetch('/post-stubbi', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
    console.log(data); // log the response from the server
    if (data.success) {

        // handle the case where success is true
        console.log('Post was successful');
        if (addPostOverlay) {
        document.body.removeChild(addPostOverlay);
        }
    } else {
        // handle the case where success is false
        console.log(data.error);
    }
    })
    .catch(error => console.error(error));
}
});