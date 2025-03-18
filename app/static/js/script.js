function updateNumber() {
    fetch('/update')
        .then(response => response.json())
        .then(data => {
            document.getElementById("gameNumber").innerText = data.number;
        })
        .catch(error => console.error('Error:', error));
}

setInterval(updateNumber, 1000);
window.onload = updateNumber;
