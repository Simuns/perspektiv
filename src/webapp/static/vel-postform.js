let addPostOverlay;
let userContentWritten;
// get the div with class "post"
const postDiv = document.querySelector('.post img');

// add click event listener to postDiv
postDiv.addEventListener('click', async () => {
  // fetch HTML from "/vel-postform"
  const response = await fetch('/vel-postform');
  const html = await response.text();
  
  // create addPost-overlay div and insert fetched HTML
  addPostOverlay = document.createElement('div');
  addPostOverlay.id = 'addPost-overlay'; // set the id to 'addPost-overlay'
  addPostOverlay.innerHTML = html;
  
  // add addPost-overlay to the DOM
  document.body.appendChild(addPostOverlay);

  // ONLY ADD CSS IF IT IS NOT ALREADY PRESENT IN SITE
  const cssLink = document.querySelector('link[href="/static/vel-postform.css"]');
  if (!cssLink) {
    const newCssLink = document.createElement('link');
    newCssLink.rel = 'stylesheet';
    newCssLink.href = '/static/vel-postform.css';
    document.head.appendChild(newCssLink);}

  const overlayDiv = document.querySelector('.overlay');
  // add and load script
  const script = document.createElement('script');
  script.src = '/static/activate-postform.js'; // replace with the path to your script file
  document.head.appendChild(script);
  // add click event listener to addPost-overlay

  overlayDiv.addEventListener('click', (event) => {
    // check if the clicked element is the addPostOverlay div itself
    if (event.target === overlayDiv) {
      if (userContentWritten) {
        showPopup("Er tú viss/ur um at tú ynskir at fara úr?", function() {
          // Code to execute if the user clicks "Yes"
          document.body.removeChild(addPostOverlay);});
      } else {
        // remove addPost-overlay from the DOM
        document.body.removeChild(addPostOverlay);
      }
    }
  });
});
