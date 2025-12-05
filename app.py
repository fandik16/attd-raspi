import RPi.GPIO as GPIO
from pn532 import *
import requests
import cv2
import tempfile
import os
import time
import threading

from config import API_URL, DEVICE_NAME, APP_VERSION
from picamera2 import Picamera2


# =========================
# GLOBAL FLAG
# =========================
RUNNING = True


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


threading.Thread(target=led_worker, daemon=True).start()


# =========================
# SETUP BUTTON D6
# =========================
BUTTON_PIN = 6
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# =========================
# SETUP CAMERA
# =========================
picam2 = Picamera2()

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


# =========================
# FUNGSI KONVERSI UID
# =========================
def uid_to_decimal(uid):
    try:
        hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
        return str(int(hex_str, 16)).zfill(10)
    except Exception:
        return "0000000000"


# =========================
# FUNGSI CAPTURE GAMBAR
# =========================
def capture_image_file():
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


# =========================
# BRIGHTNESS CONTROL + TOUCHSCREEN DRIVER
# =========================
BRIGHTNESS_IS_ON = True
AUTO_OFF_SECONDS = 300
LAST_SCAN = time.time()


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


# Nyalakan brightness saat startup
set_brightness(255)


# =========================
# BUTTON WORKER (D6 toggle brightness)
# =========================
def button_worker():
    global LAST_SCAN, BRIGHTNESS_IS_ON, RUNNING

    while RUNNING:
        try:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15)  # debounce

                if GPIO.input(BUTTON_PIN) == GPIO.LOW:

                    if BRIGHTNESS_IS_ON:
                        set_brightness(0)
                    else:
                        set_brightness(255)

                    LAST_SCAN = time.time()
                    time.sleep(0.5)  # reset tombol

        except Exception:
            break

        time.sleep(0.02)


threading.Thread(target=button_worker, daemon=True).start()


# =========================
# MAIN PROGRAM
# =========================
if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        try:
            pn532.SAM_configuration()
        except Exception as e:
            print("Gagal konfigurasi PN532:", e)

        print("Application Version", APP_VERSION)
        print("Tempelkan kartu...")

        while True:

            # === Auto Off ===
            if BRIGHTNESS_IS_ON and (time.time() - LAST_SCAN >= AUTO_OFF_SECONDS):
                set_brightness(0)
                print("Brightness OFF (auto)")

            # === Scan kartu ===
            try:
                uid = pn532.read_passive_target(timeout=0.5)
            except Exception:
                print("PN532 error: retrying...")
                time.sleep(0.5)
                continue

            if uid is None:
                continue

            # === Kartu ditemukan ===
            set_brightness(255)
            LAST_SCAN = time.time()

            card_decimal = uid_to_decimal(uid)
            print("Reading Card:", card_decimal)

            # === Ambil foto ===
            img_path = capture_image_file()
            if img_path is None:
                LED_MODE = "FAIL"
                continue

            # === Upload ke server ===
            try:
                with open(img_path, "rb") as img_file:
                    files = {"leave_letter": ("image.jpg", img_file, "image/jpeg")}
                    data = {"device_name": DEVICE_NAME, "card_number": card_decimal}
                    response = requests.post(API_URL, data=data, files=files, timeout=15)

                status = response.status_code

            except Exception as e:
                print("Gagal upload:", e)
                LED_MODE = "FAIL"
                status = None

            finally:
                try:
                    os.remove(img_path)
                except:
                    pass

            print("Status:", status)

            # === PROCESS RESPONSE ===
            if status is None:
                continue

            try:
                data_json = response.json()
            except:
                print("Response bukan JSON!")
                LED_MODE = "FAIL"
                continue

            if status == 200:
                LED_MODE = "OK"
                print(data_json.get("name"))
                print(data_json.get("time"))

            elif status == 404:
                LED_MODE = "FAIL"
                print("RFID card not found")

            else:
                LED_MODE = "FAIL"
                print("Error:", data_json)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")

    finally:
        RUNNING = False
        time.sleep(0.2)  # beri waktu thread berhenti

        GPIO.cleanup()
        try:
            picam2.stop()
        except:
            pass

        print("GPIO Clear, Camera Stopped")
