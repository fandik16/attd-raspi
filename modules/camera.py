import cv2
import tempfile
from picamera2 import Picamera2

picam2 = Picamera2()

camera_config = picam2.create_still_configuration(
    main={"size": (1280, 720)},
    buffer_count=2
)

picam2.configure(camera_config)
picam2.start()

try:
    picam2.set_controls({"AfMode": 2})
except:
    pass


def capture_image():
    """Ambil gambar & return file path"""
    try:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print("Gagal capture:", e)
        return None

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    cv2.imwrite(temp.name, frame)
    return temp.name


def stop_camera():
    picam2.stop()
