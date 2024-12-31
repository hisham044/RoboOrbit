let intervalId;
    
// Function to start sending commands continuously
function startSendingCommand(direction) {
    sendCommand(direction);
    intervalId = setInterval(() => sendCommand(direction), 100); // Adjust the interval as needed
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

        // Combined mousedown and touchstart for starting the command
        const startHandler = (event) => {
            event.preventDefault(); // Prevent default browser actions
            startSendingCommand(direction);
        };

        // Combined mouseup, mouseleave, and touchend for stopping the command
        const stopHandler = () => {
            stopSendingCommand();
        };

        button.addEventListener('mousedown', startHandler);
        button.addEventListener('touchstart', startHandler);

        button.addEventListener('mouseup', stopHandler);
        button.addEventListener('mouseleave', stopHandler);
        button.addEventListener('touchend', stopHandler);
    });
});

// Fullscreen toggle function
function toggleFullscreen() {
    const videoContainer = document.getElementById('video-container');
    const fullscreenBtn = document.getElementById('fullscreen-btn');

    if (!document.fullscreenElement) {
        videoContainer.requestFullscreen();
        fullscreenBtn.textContent = "🔲"; // Icon for exiting fullscreen
    } else {
        document.exitFullscreen();
        fullscreenBtn.textContent = "🔳"; // Icon for entering fullscreen
    }
}

// Ensure controls and button visibility persist in fullscreen mode
document.addEventListener('fullscreenchange', () => {
    const overlay = document.getElementById('overlay');
    overlay.style.display = document.fullscreenElement ? 'flex' : 'flex';
});