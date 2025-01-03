
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


# qr_scanner.py updates
class QRScanner:
    def __init__(self, camera, distance_sensor):
        self.camera = camera
        self.distance_sensor = distance_sensor
        self.last_scan_result = None
        self.scan_timestamp = None
        self.popup_active = False
        self.popup_start_time = None
        self.MIN_POPUP_DURATION = 5  # seconds

    def get_scan_result(self):
        if self.last_scan_result and time.time() - self.scan_timestamp < 5:
            return self.last_scan_result
        return None

    def process_frame(self):
        frame = self.camera.capture_frame()
        if frame is None:
            return None

        # # Flip the frame vertically
        # frame = cv2.flip(frame, 0)

        # Define the area for processing (focused rectangle)
        h, w = frame.shape[:2]
        qr_size = min(w, h) // 2
        x1 = (w - qr_size) // 2
        y1 = (h - qr_size) // 2
        x2 = x1 + qr_size
        y2 = y1 + qr_size
        qr_roi = frame[y1:y2, x1:x2]

        # Convert to grayscale
        gray = cv2.cvtColor(qr_roi, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Increase contrast using histogram equalization
        equalized = cv2.equalizeHist(blurred)

        # Sharpen the image
        kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])
        sharpened = cv2.filter2D(equalized, -1, kernel)

        # Apply adaptive thresholding
        thresholded = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Decode QR codes
        qr_codes = pyzbar.decode(thresholded)
        for qr in qr_codes:
            self.last_scan_result = qr.data.decode('utf-8')
            self.scan_timestamp = time.time()

        # Draw the rectangle and place the processed ROI back into the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        frame[y1:y2, x1:x2] = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes() if ret else None

    