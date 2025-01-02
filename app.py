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
import threading
import queue

app = Flask(__name__)

# Existing setup
bus = smbus2.SMBus(1)
arduino_address = 0x08
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


# New setup for QR scanning
DISTANCE_THRESHOLD = 30  # cm
try:
    ultrasonic = DistanceSensor(echo=17, trigger=4)
    SENSOR_ENABLED = True
except Exception as e:
    print(f"Error initializing distance sensor: {e}")
    SENSOR_ENABLED = False

# Queue for distance readings
distance_queue = queue.Queue(maxsize=1)

def get_distance():
    """Get distance reading from ultrasonic sensor."""
    while True:
        try:
            if SENSOR_ENABLED:
                distance = ultrasonic.distance * 100  # Convert to cm
                # Update queue with latest reading
                try:
                    distance_queue.get_nowait()  # Remove old value if exists
                except queue.Empty:
                    pass
                distance_queue.put(distance)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error reading distance: {e}")
            time.sleep(1)

# Start distance reading thread
distance_thread = threading.Thread(target=get_distance, daemon=True)
distance_thread.start()

def get_current_distance():
    """Get the most recent distance reading."""
    try:
        return distance_queue.get_nowait()
    except queue.Empty:
        return None


@app.route('/qr-scan')
def qr_scan():
    return render_template('qr_scan.html')

def gen_qr():
    """Generate frames for QR scanning page."""
    last_qr_time = 0
    student_id = None
    show_student_id = False
    
    while True:
        frame = picam.capture_array()
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        
        # Get current time and distance
        current_time = datetime.now().strftime("%H:%M:%S")
        distance = get_current_distance()
        
        # Add time overlay
        cv2.putText(frame, current_time, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add distance overlay or error message
        if distance is not None:
            distance_text = f"Distance: {distance:.1f} cm"
            cv2.putText(frame, distance_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Show QR scanning overlay when person is detected
            if distance <= DISTANCE_THRESHOLD:
                h, w = frame.shape[:2]
                qr_size = min(w, h) // 2
                x1 = (w - qr_size) // 2
                y1 = (h - qr_size) // 2
                x2 = x1 + qr_size
                y2 = y1 + qr_size
                
                # Draw semi-transparent overlay
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), 2)
                frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
                
                # Scan for QR codes
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                qr_codes = pyzbar.decode(gray)
                
                for qr in qr_codes:
                    student_id = qr.data.decode('utf-8')
                    last_qr_time = time.time()
                    show_student_id = True
        else:
            cv2.putText(frame, "Error: Distance sensor not available",
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Show student ID for 3 seconds after scanning
        if show_student_id and time.time() - last_qr_time < 3:
            cv2.putText(frame, f"Student ID: {student_id}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif show_student_id:
            show_student_id = False
            student_id = None
        
        # Convert frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed_qr')
def video_feed_qr():
    return Response(gen_qr(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
