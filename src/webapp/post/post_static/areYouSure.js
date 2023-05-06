function showPopup(message, yesCallback, noCallback) {
    const popup = document.createElement('div');
    popup.style.display = 'none';
    popup.style.position = 'fixed';
    popup.style.top = '0';
    popup.style.bottom = '0';
    popup.style.left = '0';
    popup.style.right = '0';
    popup.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    popup.style.zIndex = '9999';
    popup.style.flexDirection = 'column';
    popup.style.borderRadius = "15px"
    //flex-direction: column;
    
    // Set the popup's width and height
    popup.style.width = '300px';
    popup.style.height = '200px';
    
    // Center the popup both horizontally and vertically
    popup.style.transform = 'translate(-50%, -50%)';
    popup.style.top = '50%';
    popup.style.left = '50%';
    document.body.appendChild(popup);
  
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    messageElement.style.color = '#fff';
    messageElement.style.textAlign = 'center';
    messageElement.style.marginTop = '30px';
    popup.appendChild(messageElement);
  
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.display = 'inline-flex';
    buttonsContainer.style.justifyContent = 'center';
    buttonsContainer.style.marginTop = '30px';
    popup.appendChild(buttonsContainer);
  
    const yesButton = document.createElement('button');
    yesButton.textContent = 'Ja';
    yesButton.style.marginRight = '20px';
    yesButton.style.padding = '10px 20px';
    yesButton.style.borderRadius = '5px';
    yesButton.style.backgroundColor = '#fff';
    yesButton.style.color = '#000';
    yesButton.style.border = 'none';
    yesButton.style.cursor = 'pointer';
    buttonsContainer.appendChild(yesButton);
  
    const noButton = document.createElement('button');
    noButton.textContent = 'Nei';
    noButton.style.padding = '10px 20px';
    noButton.style.borderRadius = '5px';
    noButton.style.backgroundColor = '#fff';
    noButton.style.color = '#000';
    noButton.style.border = 'none';
    noButton.style.cursor = 'pointer';
    buttonsContainer.appendChild(noButton);
  
    yesButton.addEventListener('click', function () {
      if (typeof yesCallback === 'function') {
        yesCallback();
      }
      document.body.removeChild(popup);
    });
  
    noButton.addEventListener('click', function () {
      if (typeof noCallback === 'function') {
        noCallback();
      }
      document.body.removeChild(popup);
    });
  
    popup.style.display = 'flex';
  }
  