import os
import smbus2
import time
import numpy as np
from picamera2 import Picamera2
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# I2C setup (using the default I2C bus)
bus = smbus2.SMBus(1)  # 1 is the default bus for Raspberry Pi
arduino_address = 0x08  # Arduino's I2C address

# Initialize Picamera2
picam = Picamera2()
picam.preview_configuration.main.size = (684, 385)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

def send_command_to_arduino(command):
    """Send a command to the Arduino via I2C."""
    try:
        bus.write_byte(arduino_address, command)
        print(f"Command {command} sent to Arduino.")
    except Exception as e:
        print(f"Error sending command to Arduino: {e}")

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    """Generate frames from the Picamera2 for streaming."""
    while True:
        frame = picam.capture_array()
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move/<direction>')
def move(direction):
    command_dict = {
        'stop': 0,
        'move_forward': 1,
        'move_left': 2,
        'move_right': 3,
        'move_backward': 4,
        'camera_up': 5,
        'camera_down': 6,
        'open_delivery': 7,
        'close_delivery': 8,
    }
    command = command_dict.get(direction, 0)  # Default to stop if invalid direction
    send_command_to_arduino(command)
    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
