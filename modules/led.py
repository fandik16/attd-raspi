import RPi.GPIO as GPIO
import threading
import time

LED_PIN = None
LED_MODE = "IDLE"
RUNNING = False

_thread = None
_lock = threading.Lock()
_stop_event = threading.Event()


def init_led(pin: int):
    """Dipanggil dari main.py untuk inisialisasi LED."""
    global LED_PIN, RUNNING

    LED_PIN = pin
    RUNNING = True

    # Set mode jika belum diset
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BCM)

    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)


def _led_worker():
    global LED_MODE, RUNNING, LED_PIN

    while not _stop_event.is_set():
        try:
            with _lock:
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

                with _lock:
                    LED_MODE = "IDLE"

            elif mode == "FAIL":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN, GPIO.LOW)

                with _lock:
                    LED_MODE = "IDLE"

            else:
                with _lock:
                    LED_MODE = "IDLE"
                time.sleep(0.1)

        except Exception:
            break


def start_led_thread():
    """Mulai thread setelah init_led() dipanggil."""
    global _thread
    if _thread and _thread.is_alive():
        return

    _stop_event.clear()
    _thread = threading.Thread(target=_led_worker, daemon=True)
    _thread.start()


def stop_led():
    """Hentikan LED dan cleanup."""
    global RUNNING

    RUNNING = False
    _stop_event.set()

    try:
        if _thread:
            _thread.join(timeout=1)
    except:
        pass

    try:
        if LED_PIN is not None:
            GPIO.output(LED_PIN, GPIO.LOW)
    except:
        pass


def set_led_mode(mode: str):
    """Set mode LED."""
    global LED_MODE
    mode = mode.upper()

    if mode not in ["IDLE", "OK", "FAIL"]:
        raise ValueError("Invalid LED mode")

    with _lock:
        LED_MODE = mode


def get_led_mode():
    with _lock:
        return LED_MODE
