window.onscroll = function() {
    if ((window.innerHeight + Math.ceil(window.pageYOffset)) >= document.body.offsetHeight) {
        // Get the last div element with the class floating-box
        var floatingBoxes = document.getElementsByClassName("floatingBox");
        var lastFloatingBox = floatingBoxes[floatingBoxes.length - 1];
        var lastFloatingBoxId = lastFloatingBox.getAttribute("id");
        console.log('Last floating box ID:', lastFloatingBoxId);

        // Send the ID to /index_loadMore using AJAX
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                // Place the new content above the existing content
                var newContent = this.responseText;
                var placeholder = document.getElementById("placeholder");
                placeholder.insertAdjacentHTML('beforebegin', newContent);            }
        };
        xhttp.open("POST", "/index_loadMore", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("lastFloatingBoxId=" + lastFloatingBoxId);
    }
};