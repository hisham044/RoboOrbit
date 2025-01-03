
# distance_sensor.py
from gpiozero import DistanceSensor
import threading
import queue
import time

class DistanceSensorManager:
    def __init__(self, echo_pin=17, trigger_pin=4):
        self.distance_queue = queue.Queue(maxsize=1)
        try:
            self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
            self.sensor_enabled = True
        except Exception as e:
            print(f"Error initializing distance sensor: {e}")
            self.sensor_enabled = False
        
        self.start_monitoring()

    def start_monitoring(self):
        self.monitor_thread = threading.Thread(target=self._monitor_distance, daemon=True)
        self.monitor_thread.start()

    def _monitor_distance(self):
        while True:
            try:
                if self.sensor_enabled:
                    distance = self.sensor.distance * 100  # Convert to cm
                    try:
                        self.distance_queue.get_nowait()  # Remove old value
                    except queue.Empty:
                        pass
                    self.distance_queue.put(distance)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error reading distance: {e}")
                time.sleep(1)

    def get_current_distance(self):
        try:
            return self.distance_queue.get_nowait()
        except queue.Empty:
            return None
