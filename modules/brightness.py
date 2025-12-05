import os
import time

BRIGHTNESS_PATH = "/sys/class/backlight/11-0045/brightness"
BRIGHTNESS_IS_ON = True
LAST_SCAN = time.time()
AUTO_OFF_SECONDS = 300


def brightness_on():
    global BRIGHTNESS_IS_ON
    os.system(f"echo 255 | sudo tee {BRIGHTNESS_PATH}")
    BRIGHTNESS_IS_ON = True


def brightness_off():
    global BRIGHTNESS_IS_ON
    os.system(f"echo 0 | sudo tee {BRIGHTNESS_PATH}")
    BRIGHTNESS_IS_ON = False


def brightness_auto_check():
    global LAST_SCAN
    if BRIGHTNESS_IS_ON and (time.time() - LAST_SCAN >= AUTO_OFF_SECONDS):
        brightness_off()
        print("Brightness OFF (auto)")


def update_last_scan():
    global LAST_SCAN
    LAST_SCAN = time.time()
