# modules/rfid.py
import time
import os
from pn532 import *
import cv2
import tempfile

from config import API_URL, DEVICE_NAME, APP_VERSION
from modules.utils import uid_to_decimal
from modules.brightness import BrightnessControl
from modules.utils import TouchControl
from modules.camera import WebCamera
from modules.uploader import Uploader
from modules.led import LED_MODE

brightness = BrightnessControl()
touch = TouchControl()
uploader = Uploader()
camera = WebCamera()

camera.start()

AUTO_OFF = 300
LAST_SCAN = time.time()
BRIGHTNESS_ON = True

os.system("echo 255 | sudo tee /sys/class/backlight/11-0045/brightness")


class RFIDWorker:
    def __init__(self):
        self.pn = PN532_SPI(debug=False, reset=20, cs=4)
        self.pn.SAM_configuration()

        print("App Version:", APP_VERSION)
        print("Ready to Scan...")

    def run(self):
        global LAST_SCAN, BRIGHTNESS_ON, LED_MODE

        while True:
            if BRIGHTNESS_ON and (time.time() - LAST_SCAN >= AUTO_OFF):
                brightness.set(0)
                touch.disable()
                BRIGHTNESS_ON = False
                print("Auto OFF Screen")

            uid = self.pn.read_passive_target(timeout=0.5)
            if uid is None:
                continue

            brightness.set(255)
            touch.enable()
            BRIGHTNESS_ON = True
            LAST_SCAN = time.time()

            card = uid_to_decimal(uid)
            print("Card:", card)

            img = camera.get_frame_jpeg()
            if img is None:
                continue

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            with open(tmp.name, "wb") as f:
                f.write(img)

            resp = uploader.send(API_URL, DEVICE_NAME, card, tmp.name)

            os.remove(tmp.name)

            if resp is None:
                LED_MODE = "FAIL"
                continue

            if resp.status_code == 200:
                LED_MODE = "OK"
                print(resp.json())
            else:
                LED_MODE = "FAIL"
                print("ERR:", resp.text)

            time.sleep(2)
