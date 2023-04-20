const editDivs = document.querySelectorAll('.edit');
let originalEditDiv;
let editOpenDiv;

// Function to add the click event listener to an "edit" div
function addEditDivEventListener(editDiv) {
  editDiv.addEventListener('click', () => {
    // Close other open box if one is opened already
    if (typeof originalEditDiv !== 'undefined') {
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
        editDiv.replaceWith(editOpenDiv);

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

// Loop through each "edit" div and add the click event listener
editDivs.forEach(editDiv => {
  addEditDivEventListener(editDiv);
});
