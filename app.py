# app.py
import os
import smbus2
import time
import numpy as np
from picamera2 import Picamera2
from flask import Flask, render_template, Response, jsonify
import cv2
from datetime import datetime
from gpiozero import DistanceSensor
import pyzbar.pyzbar as pyzbar

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
        'increase_speed': 9,
        'decrease_speed': 10
    }
    command = command_dict.get(direction, 0)  # Default to stop if invalid direction
    send_command_to_arduino(command)
    return '', 200


# Initialize ultrasonic sensor
ultrasonic = DistanceSensor(echo=17, trigger=4)

# Global variables
DISTANCE_THRESHOLD = 30  # cm
QR_DISPLAY_TIME = 3  # seconds
last_qr_time = 0
last_qr_data = None
is_person_detected = False

def get_distance():
    """Get distance reading from ultrasonic sensor."""
    return ultrasonic.distance * 100  # Convert to cm

def detect_qr_code(frame):
    """Detect and decode QR codes in the frame."""
    decoded_objects = pyzbar.decode(frame)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode('utf-8')
    return None

def draw_overlay(frame, distance):
    """Draw time and distance overlay on frame."""
    height, width = frame.shape[:2]
    
    # Add semi-transparent overlay
    overlay = frame.copy()
    
    # Draw time and distance
    current_time = datetime.now().strftime("%H:%M:%S")
    cv2.putText(overlay, f"Time: {current_time}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(overlay, f"Distance: {distance:.1f} cm", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Draw QR code guide if person detected
    if is_person_detected:
        # Calculate center square
        square_size = min(width, height) // 2
        x = (width - square_size) // 2
        y = (height - square_size) // 2
        
        # Draw semi-transparent overlay
        cv2.rectangle(overlay, (x, y), (x + square_size, y + square_size),
                     (0, 255, 0), 2)
        cv2.putText(overlay, "Position QR Code Here", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # If QR code was recently detected, show the data
    global last_qr_time, last_qr_data
    if time.time() - last_qr_time < QR_DISPLAY_TIME and last_qr_data:
        cv2.putText(overlay, f"Student ID: {last_qr_data}", (width//4, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    
    # Blend the overlay with the original frame
    alpha = 0.7
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    return frame

def gen2():
    """Generate frames from the camera with overlay."""
    global is_person_detected, last_qr_time, last_qr_data
    
    while True:
        # Capture frame
        frame = picam.capture_array()
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        
        # Get distance reading
        distance = get_distance()
        
        # Update person detection state
        is_person_detected = distance < DISTANCE_THRESHOLD
        
        # If person detected, try to scan QR code
        if is_person_detected:
            qr_data = detect_qr_code(frame)
            if qr_data:
                last_qr_data = qr_data
                last_qr_time = time.time()
        
        # Add overlay to frame
        frame = draw_overlay(frame, distance)
        
        # Encode frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/qr-scan')
def qr_scan():
    return render_template('qr_scan.html')

@app.route('/video_feed2')
def video_feed2():
    return Response(gen2(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_distance')
def get_distance_route():
    return jsonify({'distance': get_distance()})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)