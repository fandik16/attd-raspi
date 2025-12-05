import os
from config import BRIGHTNESS_PATH
from modules.utils import LAST_SCAN

BRIGHTNESS_IS_ON = True

def set_brightness(level):
    global BRIGHTNESS_IS_ON

    os.system(f"echo {level} | sudo tee {BRIGHTNESS_PATH}")

    if level == 0:
        os.system("sudo rmmod edt_ft5x06")
        BRIGHTNESS_IS_ON = False
    else:
        os.system("sudo modprobe edt_ft5x06")
        BRIGHTNESS_IS_ON = True
