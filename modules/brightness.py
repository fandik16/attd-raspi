import os
import time
import threading
import RPi.GPIO as GPIO

BUTTON_PIN = 6
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
AUTO_OFF_SECONDS = 300

class BrightnessController:
    def __init__(self):
        self.is_on = True
        self.last_scan = time.time()
        self.set_brightness(255)
        threading.Thread(target=self._button_worker, daemon=True).start()

    def set_brightness(self, level):
        os.system(f"echo {level} | sudo tee /sys/class/backlight/11-0045/brightness")

        if level == 0:
            os.system("sudo rmmod edt_ft5x06")
            self.is_on = False
        else:
            os.system("sudo modprobe edt_ft5x06")
            self.is_on = True

    def turn_on(self):
        self.last_scan = time.time()
        self.set_brightness(255)

    def auto_off_check(self):
        if self.is_on and (time.time() - self.last_scan >= AUTO_OFF_SECONDS):
            self.set_brightness(0)

    def _button_worker(self):
        while True:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15)
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    if self.is_on:
                        self.set_brightness(0)
                    else:
                        self.set_brightness(255)
                    self.last_scan = time.time()
                    time.sleep(0.5)
            time.sleep(0.02)
