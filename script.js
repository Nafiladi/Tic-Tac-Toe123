function createRoom() {
    const username = prompt('Enter your name:');
    if (username) {
        fetch('/create_room', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            room = data.room;
            playerSymbol = 'X';
            initializeGame(username);
        })
        .catch(error => console.error('Error:', error)); // Add error handling
    }
}
