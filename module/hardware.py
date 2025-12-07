import RPi.GPIO as GPIO
from picamera2 import Picamera2
import os
import time
import threading
import cv2 # Diperlukan untuk konversi frame kamera ke JPEG
import tempfile

# =========================
# GLOBAL FLAG
# =========================
RUNNING = True
BRIGHTNESS_IS_ON = True
LAST_SCAN = time.time()
AUTO_OFF_SECONDS = 300

# =========================
# SETUP LED INDICATOR (D5)
# =========================
LED_PIN = 5
GPIO.setmode(GPIO.BCM)
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
            else:
                LED_MODE = "IDLE"
                time.sleep(0.1)
        except Exception:
            break

def start_led_worker():
    threading.Thread(target=led_worker, daemon=True).start()

def set_led_mode(mode):
    global LED_MODE
    LED_MODE = mode


# =========================
# SETUP CAMERA & STREAMING FUNCTIONS
# =========================
picam2 = Picamera2()

def setup_camera():
    camera_config = picam2.create_still_configuration(
        main={"size": (1280, 720)},
        buffer_count=2
    )
    picam2.configure(camera_config)
    picam2.start()
    try:
        picam2.set_controls({"AfMode": 2})
    except Exception:
        pass

def stop_camera():
    try:
        picam2.stop()
    except:
        pass

def capture_image_file():
    """Mengambil gambar dari Picamera2, mengkonversi, dan menyimpannya ke file sementara."""
    try:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print("Gagal mengambil gambar:", e)
        return None

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        cv2.imwrite(temp.name, frame)
        return temp.name
    except Exception as e:
        print("Gagal menyimpan gambar:", e)
        return None

def get_jpeg_frame():
    """Mengambil frame dari kamera, mengkonversi ke JPEG, dan mengembalikan byte."""
    try:
        # Ambil frame dari Picamera2 (RGB array)
        frame = picam2.capture_array()
        
        # Konversi RGB ke BGR (format yang digunakan OpenCV)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Kompresi frame ke format JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        
        # Kembalikan byte JPEG
        return buffer.tobytes()
        
    except Exception:
        return None 


# =========================
# BRIGHTNESS CONTROL + TOUCHSCREEN DRIVER
# =========================
def set_brightness(level):
    global BRIGHTNESS_IS_ON

    os.system(f"echo {level} | sudo tee /sys/class/backlight/11-0045/brightness")

    if level == 0:
        print("Brightness OFF → unload touchscreen driver")
        os.system("sudo rmmod edt_ft5x06")
        BRIGHTNESS_IS_ON = False
    else:
        print("Brightness ON → load touchscreen driver")
        os.system("sudo modprobe edt_ft5x06")
        BRIGHTNESS_IS_ON = True

def handle_auto_off():
    global LAST_SCAN, BRIGHTNESS_IS_ON
    if BRIGHTNESS_IS_ON and (time.time() - LAST_SCAN >= AUTO_OFF_SECONDS):
        set_brightness(0)
        print("Brightness OFF (auto)")

def update_last_scan_time():
    global LAST_SCAN
    LAST_SCAN = time.time()


# =========================
# SETUP BUTTON D6
# =========================
BUTTON_PIN = 6
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_worker():
    global RUNNING

    while RUNNING:
        try:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15)  # debounce

                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    if BRIGHTNESS_IS_ON:
                        set_brightness(0)
                    else:
                        set_brightness(255)
                    update_last_scan_time()
                    time.sleep(0.5)  # reset tombol
        except Exception:
            break
        time.sleep(0.02)

def start_button_worker():
    threading.Thread(target=button_worker, daemon=True).start()


def cleanup_hardware():
    global RUNNING
    RUNNING = False
    time.sleep(0.2)
    GPIO.cleanup()
    stop_camera()
    print("GPIO Clear, Camera Stopped")

# Nyalakan brightness saat startup
set_brightness(255)