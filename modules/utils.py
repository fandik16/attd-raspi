# modules/utils.py
import RPi.GPIO as GPIO
import time
import os
from modules.brightness import BrightnessControl

BUTTON_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class TouchControl:
    def enable(self):
        print("Touchscreen ENABLE")
        os.system("sudo modprobe edt_ft5x06")

    def disable(self):
        print("Touchscreen DISABLE")
        os.system("sudo rmmod edt_ft5x06")


brightness = BrightnessControl()
touch = TouchControl()


class ButtonWatcher:
    def run(self):
        while True:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:

                curr = brightness.get()

                if curr == 0:
                    brightness.set(255)
                    touch.enable()
                    print("Button → Brightness ON")
                else:
                    brightness.set(0)
                    touch.disable()
                    print("Button → Brightness OFF")

                time.sleep(0.5)  # debounce

            time.sleep(0.05)


def uid_to_decimal(uid):
    hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
    return str(int(hex_str, 16)).zfill(10)
