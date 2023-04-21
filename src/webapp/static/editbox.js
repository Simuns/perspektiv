
const editDivs = document.querySelectorAll('.edit');
let originalEditDiv;
let editOpenDiv;





// Function to add the click event listener to an "edit" div
function addEditDivEventListener(editDiv, isFormSubmitted) {
  editDiv.addEventListener('click', () => {
    // Close other open box if one is opened already if content has not been changed
    if (typeof originalEditDiv !== 'undefined') {
      // Verify if the original form has changed, without being saved

      // example usage of the variable outside the event listener
      if (isFormSubmitted) {
        console.log('Form data was successfully submitted');
      } else {
        console.log('Form data was not submitted');
        var editOpenForm = editOpenDiv.querySelector('form');
        console.log(editOpenForm);
        
        if (hasFormChanged(editOpenForm)) {
          console.log("HALT form has changed yet we cannot move");
          return;
        }
      }
      //// REPLACE THE ACTUAL EDITDIV WITH ORIGINAL CONTENT ////
      editOpenDiv.replaceWith(originalEditDiv);

    }
    originalEditDiv = editDiv.cloneNode(true);

    const id = editDiv.id;

    fetch(`/um_meg/open?id=${id}`)
      .then(response => response.text())
      .then(data => {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = data;
        editOpenDiv = tempDiv.querySelector(`#${id}.edit-open`);
        // ADD CONTENT TO CLICKED DIV
        editDiv.replaceWith(editOpenDiv);


        const closeButton = editOpenDiv.querySelector('.closeKnappur');
        closeButton.addEventListener('click', function(event) {
          event.preventDefault(); // prevent default button behavior
          editOpenDiv.replaceWith(originalEditDiv)
        });
        // ADD EVENT LISTENER TO SUBMIT BUTTON AND TIE TO POST ACTION
        const editOpenForm = editOpenDiv.querySelector('form');
        const submitBtn = editOpenDiv.querySelector('.goymKnappur');
        let isFormSubmitted = false; // variable to track if the form is submitted
        submitBtn.addEventListener('click', function(event) {
          event.preventDefault(); // prevent default button behavior
        
          const formData = new FormData(editOpenForm); // create a new FormData object from the form
        
          // send a POST request using the fetch() API
          fetch('/um_meg', {
            method: 'POST',
            body: formData
          })
          .then(response => response.text())
          .then(data => {
            console.log(data); // log the response from the server
            isFormSubmitted = true; // set the variable to true on successful form submission
          })
          .catch(error => {
            console.error(error); // log any errors that occur
          });
        });

        // Execute any scripts in the new content
        const scripts = editOpenDiv.getElementsByTagName("script");
        for (let i = 0; i < scripts.length; i++) {
          const script = document.createElement("script");
          if (scripts[i].src) {
            script.src = scripts[i].src;
          } else {
            script.innerHTML = scripts[i].innerHTML;
          }
          document.body.appendChild(script);
        }

        // Add the event listener to the replaced "edit" div
        addEditDivEventListener(originalEditDiv);
      });
  });
}


// This function checks if form has been changed.
function hasFormChanged(form) {
  // Loop through all form fields
  for (var i = 0; i < form.elements.length; i++) {
    var field = form.elements[i];
    // Check if field is an input, select, or textarea
    if (field.tagName.toLowerCase() == 'input' ||
        field.tagName.toLowerCase() == 'select' ||
        field.tagName.toLowerCase() == 'textarea') {
      // Check if field value is different from original value
      if (field.value != field.defaultValue) {
        console.log("form has changed");
        return true;
      }
    }
  }
  console.log("form has not changed");
  return false;
}




// Loop through each "edit" div and add the click event listener
editDivs.forEach(editDiv => {
  addEditDivEventListener(editDiv);
});
