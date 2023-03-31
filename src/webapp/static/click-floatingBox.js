const floatingBoxes = document.querySelectorAll('.floatingBox');

floatingBoxes.forEach(box => {
  // Define the function to restore the original content
  function restoreOriginalContent() {
    box.innerHTML = box.getAttribute('data-content');
    box.classList.remove('open');
  }

  box.addEventListener('click', () => {
    // Check if the box is already open
    if (box.classList.contains('open')) {
      restoreOriginalContent();
      return;
    }

    const boxId = box.id;
    fetch(`/brøv/${boxId}`)
      .then(response => response.text())
      .then(html => {
        // Parse the HTML string
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Add the link to the CSS file
        const cssLink = doc.createElement('link');
        cssLink.setAttribute('rel', 'stylesheet');
        cssLink.setAttribute('href', '/static/article.css');
        doc.head.appendChild(cssLink);

        // Get the desired element
        const boxContent = doc.querySelector('.art');

        // Replace the box content with the new content
        box.setAttribute('data-content', box.innerHTML);
        box.innerHTML = boxContent.innerHTML;

        // Add the "open" class to the box
        box.classList.add('open');
      });
  });

  box.style.cursor = 'pointer';
});
