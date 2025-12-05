import cv2
import tempfile
from picamera2 import Picamera2

class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration(main={"size": (1280, 720)}, buffer_count=2)
        self.picam2.configure(config)
        self.picam2.start()

        try:
            self.picam2.set_controls({"AfMode": 2})
        except:
            pass

    def capture_image(self):
        try:
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        except Exception:
            return None

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        cv2.imwrite(temp.name, frame)
        return temp.name
