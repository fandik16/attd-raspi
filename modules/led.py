import threading
import time
import RPi.GPIO as GPIO
from modules.utils import RUNNING

LED_PIN = 5
GPIO.setup(LED_PIN, GPIO.OUT)

LED_MODE = "IDLE"


def led_worker():
    global LED_MODE, RUNNING

    while RUNNING:
        try:
            mode = LED_MODE

            if mode == "IDLE":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.005)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(2)

            elif mode == "OK":
                for _ in range(2):
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(LED_PIN, GPIO.LOW)
                    time.sleep(0.1)
                LED_MODE = "IDLE"

            elif mode == "FAIL":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN, GPIO.LOW)
                LED_MODE = "IDLE"

        except Exception:
            break


def start_led_thread():
    threading.Thread(target=led_worker, daemon=True).start()


def set_led_mode(mode):
    global LED_MODE
    LED_MODE = mode
