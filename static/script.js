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

// Updated fullscreen toggle function
function toggleFullscreen() {
    const videoContainer = document.getElementById('video-container');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const fullscreenIcon = fullscreenBtn.querySelector('i');

    if (!document.fullscreenElement) {
        videoContainer.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable fullscreen: ${err.message}`);
        });
        fullscreenIcon.classList.remove('fa-expand');
        fullscreenIcon.classList.add('fa-compress');
    } else {
        document.exitFullscreen().catch(err => {
            console.log(`Error attempting to exit fullscreen: ${err.message}`);
        });
        fullscreenIcon.classList.remove('fa-compress');
        fullscreenIcon.classList.add('fa-expand');
    }
}

// Enhanced fullscreen change event handler
document.addEventListener('fullscreenchange', () => {
    const overlay = document.getElementById('overlay');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const fullscreenIcon = fullscreenBtn.querySelector('i');
    
    if (document.fullscreenElement) {
        overlay.style.display = 'flex';
        fullscreenIcon.classList.remove('fa-expand');
        fullscreenIcon.classList.add('fa-compress');
    } else {
        overlay.style.display = 'flex';
        fullscreenIcon.classList.remove('fa-compress');
        fullscreenIcon.classList.add('fa-expand');
    }
});

// Attach event listeners to buttons for continuous commands
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        const direction = button.getAttribute('data-direction');

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
});