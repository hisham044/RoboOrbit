
# qr_scanner.py
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
from datetime import datetime
import time

class ScannerState:
    def __init__(self, distance_threshold=30, activation_threshold=5, scanning_timeout=10):
        self.scanning_active = False
        self.last_active_time = 0
        self.consecutive_no_person = 0
        self.DISTANCE_THRESHOLD = distance_threshold
        self.ACTIVATION_THRESHOLD = activation_threshold
        self.SCANNING_TIMEOUT = scanning_timeout

    def update(self, distance):
        current_time = time.time()
        
        if distance <= self.DISTANCE_THRESHOLD:
            self.scanning_active = True
            self.last_active_time = current_time
            self.consecutive_no_person = 0
        else:
            if self.scanning_active:
                if current_time - self.last_active_time > self.SCANNING_TIMEOUT:
                    self.consecutive_no_person += 1
                    if self.consecutive_no_person >= self.ACTIVATION_THRESHOLD:
                        self.scanning_active = False
                        self.consecutive_no_person = 0

        return self.scanning_active

class QRScanner:
    def __init__(self, camera, distance_sensor):
        self.camera = camera
        self.distance_sensor = distance_sensor
        self.scanner_state = ScannerState()
        self.last_qr_time = 0
        self.student_id = None
        self.show_student_id = False

    def process_frame(self):
        frame = self.camera.capture_frame()
        display_frame = frame.copy()
        h, w = frame.shape[:2]
        overlay = np.zeros((h, w, 3), dtype=np.uint8)

        # Add time overlay
        current_time = datetime.now().strftime("%H:%M:%S")
        cv2.putText(overlay, current_time, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Process distance sensor
        distance = self.distance_sensor.get_current_distance()
        scanning_active = self.scanner_state.update(distance) if distance is not None else False

        # Add distance indicator
        self._add_distance_indicator(overlay, distance, scanning_active)

        # Process QR scanning
        if scanning_active:
            self._process_qr_scanning(frame, overlay, h, w)

        # Add student ID overlay if needed
        self._add_student_id_overlay(overlay, h, w)

        # Combine frame with overlay
        display_frame = cv2.addWeighted(display_frame, 0.7, overlay, 0.3, 0)
        
        ret, jpeg = cv2.imencode('.jpg', display_frame)
        if ret:
            return jpeg.tobytes()
        return None

    def _add_distance_indicator(self, overlay, distance, scanning_active):
        box_color = (0, 255, 0) if scanning_active else (128, 128, 128)
        cv2.rectangle(overlay, (20, 60), (160, 100), box_color, -1)
        if distance is not None:
            distance_text = f"{distance:.1f} cm"
            cv2.putText(overlay, distance_text, (30, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        else:
            cv2.putText(overlay, "Sensor Error", (30, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    def _process_qr_scanning(self, frame, overlay, h, w):
        qr_size = min(w, h) // 2
        x1 = (w - qr_size) // 2
        y1 = (h - qr_size) // 2
        x2 = x1 + qr_size
        y2 = y1 + qr_size

        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(overlay, "Position QR Code Here", (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        qr_codes = pyzbar.decode(gray)
        
        for qr in qr_codes:
            self.student_id = qr.data.decode('utf-8')
            self.last_qr_time = time.time()
            self.show_student_id = True

    def _add_student_id_overlay(self, overlay, h, w):
        if self.show_student_id and time.time() - self.last_qr_time < 3:
            id_box_width = 300
            id_box_height = 60
            id_box_x = (w - id_box_width) // 2
            id_box_y = h - 100
            
            cv2.rectangle(overlay, 
                         (id_box_x, id_box_y),
                         (id_box_x + id_box_width, id_box_y + id_box_height),
                         (0, 255, 0), -1)
            
            cv2.putText(overlay, f"ID: {self.student_id}", 
                       (id_box_x + 10, id_box_y + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        elif self.show_student_id:
            self.show_student_id = False
            self.student_id = None
