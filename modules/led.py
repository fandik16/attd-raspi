import RPi.GPIO as GPIO
import time
from modules.utils import RUNNING

LED_PIN = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

LED_MODE = "IDLE"

def led_worker():
    global LED_MODE

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

        except:
            break
