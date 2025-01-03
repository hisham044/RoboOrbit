// static/script.js
let intervalId;
    
// Function playhorn (play the horn.wav file in static folder)
function playHorn() {
    const audio = new Audio('/static/horn.wav');
    audio.play();
}


// Function to start sending commands continuously
function startSendingCommand(direction) {
    sendCommand(direction);
    intervalId = setInterval(() => sendCommand(direction), 100);
}

// Function to stop sending commands
function stopSendingCommand() {
    clearInterval(intervalId);
}

// Function to send a command to the server
function sendCommand(direction) {
    $.get(`/move/${direction}`, function () {
        console.log(`Command sent: ${direction}`);
    });
}

// Attach event listeners to buttons for continuous commands
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        const direction = button.getAttribute('data-direction');

        if (!direction) {
            // Skip buttons like the horn button that don't have data-direction
            return;
        }

        const startHandler = (event) => {
            event.preventDefault();
            startSendingCommand(direction);
        };

        const stopHandler = () => {
            stopSendingCommand();
        };

        button.addEventListener('mousedown', startHandler);
        button.addEventListener('touchstart', startHandler);
        button.addEventListener('mouseup', stopHandler);
        button.addEventListener('mouseleave', stopHandler);
        button.addEventListener('touchend', stopHandler);
    });

    // Explicitly set up the horn button
    const hornButton = document.querySelector('.horn-btn');
    if (hornButton) {
        hornButton.addEventListener('click', playHorn);
    }
});