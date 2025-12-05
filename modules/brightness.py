import os
import time
import threading
import RPi.GPIO as GPIO
from modules.utils import RUNNING

BUTTON_PIN = 6
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BRIGHTNESS_IS_ON = True


def set_brightness(level):
    global BRIGHTNESS_IS_ON

    os.system(f"echo {level} | sudo tee /sys/class/backlight/11-0045/brightness")

    if level == 0:
        os.system("sudo rmmod edt_ft5x06")
        BRIGHTNESS_IS_ON = False
        print("Brightness OFF + touchscreen disabled")
    else:
        os.system("sudo modprobe edt_ft5x06")
        BRIGHTNESS_IS_ON = True
        print("Brightness ON + touchscreen enabled")


def auto_brightness_control(last_scan, timeout):
    if BRIGHTNESS_IS_ON and (time.time() - last_scan >= timeout):
        set_brightness(0)
        print("Brightness OFF (AUTO)")


def _button_worker():
    global BRIGHTNESS_IS_ON

    while RUNNING:
        try:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15)
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    if BRIGHTNESS_IS_ON:
                        set_brightness(0)
                    else:
                        set_brightness(255)

                time.sleep(0.5)

        except:
            break

        time.sleep(0.02)


def start_button_thread():
    threading.Thread(target=_button_worker, daemon=True).start()
