from picamera2 import Picamera2
import cv2
import threading
import time

class WebCamera:
    def __init__(self, size=(640, 480)):
        self.size = size
        self.picam = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Start camera only once."""
        if self.running:
            return

        try:
            self.picam = Picamera2()
            config = self.picam.create_preview_configuration(
                main={"size": self.size, "format": "RGB888"}
            )
            self.picam.configure(config)
            self.picam.start()
            self.running = True

            threading.Thread(target=self._capture_loop, daemon=True).start()
            print("Camera started")

        except Exception as e:
            print("Camera Start Error:", e)

    def _capture_loop(self):
        """Continuously read frames."""
        while self.running:
            try:
                frame = self.picam.capture_array()
                with self.lock:
                    self.frame = frame
            except:
                pass
            time.sleep(0.01)

    def get_frame(self):
        """Return latest frame as JPG."""
        if not self.running:
            self.start()

        with self.lock:
            if self.frame is None:
                return None
            _, jpeg = cv2.imencode(".jpg", self.frame)
            return jpeg.tobytes()

    def capture(self, output_path):
        """Capture still image."""
        if not self.running:
            self.start()

        frame = self.picam.capture_array()
        cv2.imwrite(output_path, frame)

    def stop(self):
        """Stop camera safely."""
        if self.running:
            try:
                self.picam.stop()
            except:
                pass

            self.running = False
            print("Camera stopped")
