import RPi.GPIO as GPIO
import time
import threading

LED_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

LED_MODE = "IDLE"


def led_worker():
    global LED_MODE
    while True:
        if LED_MODE == "IDLE":
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(2)

        elif LED_MODE == "OK":
            for _ in range(2):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.1)
            LED_MODE = "IDLE"

        elif LED_MODE == "FAIL":
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(LED_PIN, GPIO.LOW)
            LED_MODE = "IDLE"

        else:
            LED_MODE = "IDLE"
            time.sleep(0.1)


def start_led_thread():
    threading.Thread(target=led_worker, daemon=True).start()


def set_led_mode(mode):
    global LED_MODE
    LED_MODE = mode
