# camera.py
from picamera2 import Picamera2
import cv2

class Camera:
    def __init__(self):
        self.picam = Picamera2()
        self.picam.preview_configuration.main.size = (684, 385)
        self.picam.preview_configuration.main.format = "RGB888"
        self.picam.preview_configuration.align()
        self.picam.configure("preview")
        self.picam.start()

    def capture_frame(self):
        frame = self.picam.capture_array()
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        return frame

    def get_jpeg_frame(self):
        frame = self.capture_frame()
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            return jpeg.tobytes()
        return None
