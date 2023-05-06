
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
      const cssLink = document.querySelector('link[href="/post_static/post-' + postType + '.css"]');
      if (!cssLink) {
        const newCssLink = document.createElement('link');
        newCssLink.rel = 'stylesheet';
        newCssLink.href = '/post_static/post-' + postType + '.css';
        document.head.appendChild(newCssLink);}

      // Define userContentWritten and apply the script used to get pop up action
      userContentWritten = false;
      const script = document.createElement('script');
      script.src = '/post_static/areYouSure.js'; // replace with the path to your script file
      document.head.appendChild(script);

      // RUN CHARACTER COUNT IF WRITING STUBBI
      if (postType === "stubbi") {
        charCount();}

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
      //ADD SUBMIT ACTION TO POST, HANDLE DIFFERENTLY DEPENDING ON TYPE OF POST
      postButton = document.querySelector('.postButton')
      if (postButton.id === 'stubbi') {
        const script = document.createElement('script');
        script.src = '/post_static/post-stubbi.js'; // replace with the path to your script file
        document.head.appendChild(script);}
      else if (postButton.id === 'grein') {
        const script = document.createElement('script');
        script.src = '/post_static/post-grein.js'; // replace with the path to your script file
        document.head.appendChild(script);
      }
    });
  });
}
activate_postform();


// ONLY USED FOR STUBBI
function charCount() {
  const textarea = document.getElementById('stubbiTextArea');
  const charCount = document.getElementById('charCount');
  const maxLength = 365;
  
  textarea.addEventListener('input', () => {
    const remainingChars = maxLength - textarea.value.length;
    const remainingPercentage = (remainingChars / maxLength) * 100;
    charCount.innerHTML = `${remainingChars}`;

    if (remainingPercentage >= 100) {
      stubbiTextArea.style.fontSize = '3rem';} // add font size adjustment
    else if (remainingPercentage > 95) {
      stubbiTextArea.style.fontSize = '2.5rem';}
    else if (remainingPercentage > 85) {
      stubbiTextArea.style.fontSize = '2.2rem';}
    else if (remainingPercentage > 75) {
      stubbiTextArea.style.fontSize = '2.0rem';}
    else if (remainingPercentage > 65) {
      stubbiTextArea.style.fontSize = '1.8rem';}
    else if (remainingPercentage > 55) {
      stubbiTextArea.style.fontSize = '1.5rem';}
      else {
      stubbiTextArea.style.fontSize = '1.3rem';}

    if (remainingChars <= 20) {
      charCount.style.color = 'red';
      charCount.innerHTML = `${remainingChars}`;
    } else {
      charCount.style.color = 'black';
    }

    if (remainingChars < 365) {
      userContentWritten = true;
    } else {
      userContentWritten = false;
    }
  });
}
