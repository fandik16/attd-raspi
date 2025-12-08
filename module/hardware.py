# module/hardware.py

import RPi.GPIO as GPIO
import os
import time
import cv2
from picamera2 import Picamera2

# =========================
# INISIALISASI HARDWARE
# =========================
LED_PIN = 5
BUTTON_PIN = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
BRIGHTNESS_IS_ON = True

# Kamera Picamera2 (diinisialisasi sekali)
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(
    main={"size": (1280, 720)}, # Resolusi WIDE (16:9)
    buffer_count=2
)
picam2.configure(camera_config)

# =========================
# FUNGSI HARDWARE
# =========================
def start_camera():
    """Memulai kamera Picamera2."""
    try:
        picam2.start()
        picam2.set_controls({"AfMode": 2})
    except Exception as e:
        print(f"Gagal memulai kamera: {e}")

def stop_camera():
    """Menghentikan kamera Picamera2."""
    try:
        picam2.stop()
    except Exception:
        pass

def set_brightness(level):
    """Mengatur brightness layar dan memuat/membongkar driver touchscreen."""
    global BRIGHTNESS_IS_ON
    os.system(f"echo {level} | sudo tee /sys/class/backlight/11-0045/brightness")

    if level == 0 and BRIGHTNESS_IS_ON:
        os.system("sudo rmmod edt_ft5x06")
        BRIGHTNESS_IS_ON = False
        print("Brightness OFF -> driver unloaded")
    elif level > 0 and not BRIGHTNESS_IS_ON:
        os.system("sudo modprobe edt_ft5x06")
        BRIGHTNESS_IS_ON = True
        print("Brightness ON -> driver loaded")

# Atur brightness saat modul dimuat
set_brightness(255)

# =========================
# WORKER FUNCTIONS
# =========================

def led_worker(state_manager):
    """Mengontrol LED berdasarkan LED_MODE di State Manager."""
    while state_manager.RUNNING:
        try:
            mode = state_manager.LED_MODE
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
                state_manager.LED_MODE = "IDLE"
            elif mode == "FAIL":
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(LED_PIN, GPIO.LOW)
                state_manager.LED_MODE = "IDLE"
            else:
                state_manager.LED_MODE = "IDLE"
                time.sleep(0.1)
        except Exception:
            break

def button_worker(state_manager):
    """Worker untuk mengontrol brightness via tombol."""
    while state_manager.RUNNING:
        try:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15) 
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    if BRIGHTNESS_IS_ON:
                        set_brightness(0)
                    else:
                        set_brightness(255)

                    state_manager.LAST_SCAN = time.time()
                    time.sleep(0.5) 
        except Exception:
            break
        time.sleep(0.02)
        
def capture_image_array():
    """Mengambil array gambar dari kamera."""
    try:
        frame = picam2.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Gagal mengambil gambar dari kamera: {e}")
        return None