import RPi.GPIO as GPIO
import threading
import time

LED_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

class LEDController:
    def __init__(self):
        self.mode = "IDLE"
        self.running = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while self.running:
            try:
                if self.mode == "IDLE":
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    time.sleep(0.005)
                    GPIO.output(LED_PIN, GPIO.LOW)
                    time.sleep(2)

                elif self.mode == "OK":
                    for _ in range(2):
                        GPIO.output(LED_PIN, GPIO.HIGH)
                        time.sleep(0.1)
                        GPIO.output(LED_PIN, GPIO.LOW)
                        time.sleep(0.1)
                    self.mode = "IDLE"

                elif self.mode == "FAIL":
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    time.sleep(2)
                    GPIO.output(LED_PIN, GPIO.LOW)
                    self.mode = "IDLE"

                else:
                    time.sleep(0.1)

            except Exception:
                break

    def ok(self):
        self.mode = "OK"

    def fail(self):
        self.mode = "FAIL"

    def stop(self):
        self.running = False
        GPIO.cleanup()
