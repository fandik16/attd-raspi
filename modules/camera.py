from picamera2 import Picamera2
from time import sleep

picam2 = None   # jangan init langsung
preview_config = None
running = False

def start_camera():
    global picam2, preview_config, running

    if running:
        return

    try:
        picam2 = Picamera2()

        preview_config = picam2.create_preview_configuration(main={"size": (640, 360)})
        picam2.configure(preview_config)

        picam2.start()
        running = True
        sleep(0.2)

    except Exception as e:
        print("Camera start failed:", e)
        running = False


def stop_camera():
    global picam2, running

    if picam2 and running:
        try:
            picam2.stop()
        except:
            pass
        running = False


def capture_image(path):
    global picam2, running

    if not running:
        start_camera()

    try:
        picam2.capture_file(path)
        return True
    except Exception as e:
        print("Capture failed:", e)
        return False
