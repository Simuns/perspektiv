
function activate_postform() {
  // get the div with class "post"
  const postChoiseDivs = document.querySelectorAll('.val');
  mainVelPostDiv = document.querySelector('.main-velPost');

  // add click event listener to postDiv
  postChoiseDivs.forEach(postChoiseDiv => {
    postChoiseDiv.addEventListener('click', async () => {
      // do something when postChoiseDiv is clicked
      if (postChoiseDiv.id === 'stubbi') {
        // DECLARE POST TYPE AS STUBBI
        postType = "stubbi"

      } else if (postChoiseDiv.id === 'grein') {
        // DECLARE POST TYPE AS GREIN
        postType = "grein"
      }
      const response = await fetch('/post-' + postType);
      const html = await response.text();
      console.log(mainVelPostDiv);

      //backup mainvelpost for back button
      backupMainVelPostDiv = mainVelPostDiv

      // Replace the old div with the new div
      mainVelPostDiv.outerHTML = html;


      // ONLY ADD CSS IF IT IS NOT ALREADY PRESENT IN SITE
      const cssLink = document.querySelector('link[href="/static/post-' + postType + '.css"]');
      if (!cssLink) {
        const newCssLink = document.createElement('link');
        newCssLink.rel = 'stylesheet';
        newCssLink.href = '/static/post-' + postType + '.css';
        document.head.appendChild(newCssLink);}

      // Define userContentWritten and apply the script used to get pop up action
      userContentWritten = false;
      const script = document.createElement('script');
      script.src = '/static/areYouSure.js'; // replace with the path to your script file
      document.head.appendChild(script);


      // Character count
      const textarea = document.getElementById('stubbiTextArea');
      const charCount = document.getElementById('charCount');

      const maxLength = 365;
      
      textarea.addEventListener('input', () => {
        const remainingChars = maxLength - textarea.value.length;
        charCount.innerHTML = `${remainingChars}`;

        if (remainingChars <= 20) {
          charCount.style.color = 'red';
          charCount.innerHTML = `${remainingChars}`;} 
          else {
          charCount.style.color = 'black';
        }
        if (remainingChars < 365) {
          userContentWritten = true;
        } else {
          userContentWritten = false;
        }
      });
      const backButton = document.querySelector('.post-exit')
      backButton.addEventListener('click', (event) => {
        const replaceThis = document.querySelector('.postFormContainer')

        if (userContentWritten) {
          showPopup("Er tú viss/ur um at tú ynskir at fara úr?", function() {
            // Code to execute if the user clicks "Yes"
            replaceThis.outerHTML = backupMainVelPostDiv.outerHTML;
            userContentWritten = false;
            activate_postform();});
        } else {
          // remove addPost-overlay from the DOM
          replaceThis.outerHTML = backupMainVelPostDiv.outerHTML;
          activate_postform();
        }
      });
      //ADD SUBMIT ACTION
      const postButton = document.querySelector('.postButton')
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
    });
  });
}
activate_postform();

