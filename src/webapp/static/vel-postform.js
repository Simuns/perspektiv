// get the div with class "post"
const postDiv = document.querySelector('.post img');

// add click event listener to postDiv
postDiv.addEventListener('click', async () => {
  // fetch HTML from "/vel-postform"
  const response = await fetch('/vel-postform');
  const html = await response.text();
  
  // create addPost-overlay div and insert fetched HTML
  const addPostOverlay = document.createElement('div');
  addPostOverlay.id = 'addPost-overlay'; // set the id to 'addPost-overlay'
  addPostOverlay.innerHTML = html;
  
  // add addPost-overlay to the DOM
  document.body.appendChild(addPostOverlay);

  // apply the CSS file
  const cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = '/static/vel-postform.css';
  document.head.appendChild(cssLink);
  
  const overlayDiv = document.querySelector('.overlay');

  // add click event listener to addPost-overlay
  overlayDiv.addEventListener('click', (event) => {
    // check if the clicked element is the addPostOverlay div itself
    if (event.target === overlayDiv) {
      // remove addPost-overlay from the DOM
      document.body.removeChild(addPostOverlay);

      // remove the CSS file
      document.head.removeChild(cssLink);
    }
  });
});
