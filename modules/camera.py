import cv2
import tempfile
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"size": (1280, 720)},
    buffer_count=2
)

picam2.configure(config)
picam2.start()

try:
    picam2.set_controls({"AfMode": 2})
except:
    pass

def capture_image():
    try:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        cv2.imwrite(tmp.name, frame)

        return tmp.name

    except Exception as e:
        print("Camera Error:", e)
        return None

def stop_camera():
    try:
        picam2.stop()
    except:
        pass
