// Declare the variable outside the function to ensure it's only declared once
const floatingBoxes = document.querySelectorAll('.floatingBox');

// Loop through each of the floatingBox div elements
floatingBoxes.forEach(box => {
  // Add a click event listener to each box
  box.addEventListener('click', () => {
    // Get the box's ID
    const boxId = box.id;

    // Redirect to the URL with the box ID appended as a parameter
    window.location.href = `/brøv/${boxId}`;
  });
    // Add a pointer cursor when hovering over the box
    box.style.cursor = 'pointer';
});