# modules/camera.py
from picamera2 import Picamera2
import cv2

class WebCamera:
    def __init__(self, size=(1280, 720)):
        self.picam = Picamera2()
        cfg = self.picam.create_still_configuration(main={"size": size})
        self.picam.configure(cfg)

    def start(self):
        self.picam.start()

    def get_frame_jpeg(self):
        try:
            frame = self.picam.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return cv2.imencode(".jpg", frame)[1].tobytes()
        except:
            return None
