import cv2
import tempfile
from picamera2 import Picamera2


def init_camera():
    cam = Picamera2()
    config = cam.create_still_configuration(
        main={"size": (1280, 720)},
        buffer_count=2
    )

    cam.configure(config)
    cam.start()

    try:
        cam.set_controls({"AfMode": 2})
    except:
        pass

    return cam


def capture_image_file(cam):
    try:
        frame = cam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        cv2.imwrite(temp.name, frame)
        return temp.name

    except Exception as e:
        print("Gagal ambil gambar:", e)
        return None
