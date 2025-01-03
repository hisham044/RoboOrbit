// static/script.js
let intervalId;

// Function to play the horn
function playHorn() {
    const audio = new Audio('/static/horn.wav');
    audio.play();
    showOverlay('Horn');
}

// Function to start sending commands continuously
function startSendingCommand(direction) {
    sendCommand(direction);
    intervalId = setInterval(() => sendCommand(direction), 100);
    showOverlay(direction);
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

// Function to display an overlay with the current command
function showOverlay(direction) {
    const overlay = document.getElementById('overlay');
    const existingDisplay = document.getElementById('command-display');

    if (!existingDisplay) {
        const commandDisplay = document.createElement('div');
        commandDisplay.id = 'command-display';
        commandDisplay.style.position = 'absolute';
        commandDisplay.style.top = '10px';
        commandDisplay.style.right = '10px';
        commandDisplay.style.padding = '10px';
        commandDisplay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        commandDisplay.style.color = 'white';
        commandDisplay.style.fontSize = '16px';
        commandDisplay.style.borderRadius = '5px';
        overlay.appendChild(commandDisplay);
    }

    const display = document.getElementById('command-display');
    display.textContent = `Command: ${direction}`;
    setTimeout(() => (display.textContent = ''), 500); // Clear overlay after 500ms
}

// Keydown handling
document.addEventListener('keydown', (event) => {
    const keyMap = {
        ArrowUp: 'move_forward',
        ArrowDown: 'move_backward',
        ArrowLeft: 'move_left',
        ArrowRight: 'move_right',
        w: 'camera_up',
        s: 'camera_down',
        '+': 'increase_speed',
        '-': 'decrease_speed',
        o: 'open_delivery',
        c: 'close_delivery',
        p: 'stop',
        h: 'horn'
    };

    const command = keyMap[event.key];
    if (command) {
        if (command === 'horn') {
            playHorn();
        } else {
            startSendingCommand(command);
        }
    }
});

// Stop sending commands on keyup
document.addEventListener('keyup', (event) => {
    stopSendingCommand();
});

// Attach event listeners to buttons for continuous commands
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach((button) => {
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
