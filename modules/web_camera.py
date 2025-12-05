# modules/web_camera.py
import cv2
from picamera2 import Picamera2
import threading

class WebCamera:
    def __init__(self, size=(1280, 720)):
        self.picam2 = Picamera2()
        self.camera_config = self.picam2.create_still_configuration(
            main={"size": size},
            buffer_count=2
        )
        self.picam2.configure(self.camera_config)
        # lock untuk akses simultan ke kamera
        self._lock = threading.Lock()
        self._started = False

    def start(self):
        with self._lock:
            if not self._started:
                self.picam2.start()
                # coba set AF jika tersedia, jangan crash kalau tidak ada
                try:
                    self.picam2.set_controls({"AfMode": 2})
                except Exception:
                    pass
                self._started = True

    def stop(self):
        with self._lock:
            if self._started:
                try:
                    self.picam2.stop()
                except Exception:
                    pass
                self._started = False

    def get_frame_jpeg(self):
        """
        Ambil frame dari kamera, encode ke JPEG, kembalikan bytes JPEG.
        """
        with self._lock:
            if not self._started:
                # start kalau belum
                self.start()
            frame = self.picam2.capture_array()
            # Picamera2 mengembalikan frame RGB; convert ke BGR untuk OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # encode ke JPEG
            ret, jpeg = cv2.imencode('.jpg', frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ret:
                return None
            return jpeg.tobytes()
