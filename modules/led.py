import RPi.GPIO as GPIO
import time
import threading

LED_PIN = 26   # SESUAIKAN PIN LED
RUNNING = True
LED_MODE = "IDLE"

# --- FIX PENTING: SETMODE DULU ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# --- SETUP LED ---
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)


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

            else:
                LED_MODE = "IDLE"
                time.sleep(0.1)

        except Exception:
            break


def start_led_thread():
    thread = threading.Thread(target=led_worker, daemon=True)
    thread.start()


def set_led_mode(mode: str):
    global LED_MODE
    LED_MODE = mode


def stop_led():
    global RUNNING
    RUNNING = False
    time.sleep(0.1)
    GPIO.output(LED_PIN, GPIO.LOW)
