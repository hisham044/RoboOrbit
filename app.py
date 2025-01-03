# app.py
from flask import Flask, render_template, Response, jsonify, request
from config import Config
from db import db, Program, ProgramList, Student
from camera import Camera
from arduino_controller import ArduinoController
from distance_sensor import DistanceSensorManager
from qr_scanner import QRScanner
import pyttsx3
import os
import tempfile

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Initialize components
camera = Camera()
arduino = ArduinoController()
distance_sensor = DistanceSensorManager()
qr_scanner = QRScanner(camera, distance_sensor)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('voice', 'english+m1')  # Set male voice

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/drive')
def drive():
    return render_template('drive.html')

# Add this new route to app.py
@app.route('/tts', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            engine = pyttsx3.init()
            # Set properties for male voice
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # Index 0 is usually male voice
            engine.setProperty('rate', 350)    # Speed of speech
            
            # Speak the text
            engine.say(text)
            engine.runAndWait()
            return jsonify({'status': 'success', 'message': 'Text spoken successfully'})
        return jsonify({'status': 'error', 'message': 'No text provided'})
    return render_template('tts.html')

def gen():
    while True:
        frame = camera.get_jpeg_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move/<direction>')
def move(direction):
    arduino.send_command(direction)
    return '', 200

@app.route('/qr-scan')
def qr_scan():
    return render_template('qr_scan.html')

def gen_qr():
    while True:
        frame = qr_scanner.process_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed_qr')
def video_feed_qr():
    return Response(gen_qr(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/programs")
def programs():
    all_programs = Program.query.limit(10).all()
    return render_template("programs.html", programs=all_programs)

@app.route("/program/<int:program_id>")
def program_details(program_id):
    program = Program.query.get_or_404(program_id)
    program_lists = ProgramList.query.filter_by(program=program_id).all()
    student_details = [
        {
            "student": Student.query.filter_by(jamiaNo=entry.student).first(),
            "status": entry.status
        }
        for entry in program_lists
    ]
    return render_template(
        "program_details.html",
        program=program,
        student_details=student_details
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
