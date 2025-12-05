# modules/led.py
import RPi.GPIO as GPIO
import time

LED_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

LED_MODE = "IDLE"


def led_worker():
    global LED_MODE

    while True:

        if LED_MODE == "IDLE":
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(3)

        elif LED_MODE == "OK":
            for _ in range(2):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.1)
            LED_MODE = "IDLE"

        elif LED_MODE == "FAIL":
             GPIO.output(LED_PIN, GPIO.HIGH)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.LOW)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.HIGH)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.LOW)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.HIGH)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.LOW)
             time.sleep(0.1)
             GPIO.output(LED_PIN, GPIO.HIGH)
             time.sleep(2)
             GPIO.output(LED_PIN, GPIO.LOW)
             LED_MODE = "IDLE"

