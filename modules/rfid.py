# modules/rfid.py
import time
import threading
import tempfile
import os
from pn532 import PN532_SPI
from .web_camera import WebCamera
from .brightness import set_brightness
from .uploader import upload_image
from .utils import uid_to_decimal
from modules.led import set_led_mode

CAPTURE_DIR = "/home/fandik/attd/captures"

class RFIDWorker:
    def __init__(self):
        # Pastikan folder capture ada
        os.makedirs(CAPTURE_DIR, exist_ok=True)

        # Inisialisasi PN532 (SPI)
        try:
            self.pn532 = PN532_SPI(debug=False, reset=20, cs=4)
            ic, ver, rev, support = self.pn532.get_firmware_version()
            print(f"PN532 Connected — Firmware: {ver}.{rev}")
            self.pn532.SAM_configuration()
        except Exception as e:
            print("PN532 init error:", e)
            self.pn532 = None

        # Kamera instance (tidak langsung start)
        self.camera = WebCamera(size=(1280, 720))

        self.last_scan_time = time.time()
        self.running = True

    def start(self):
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        print("RFID Worker Started")

    def _loop(self):
        while self.running:
            try:
                if not self.pn532:
                    time.sleep(2)
                    continue

                uid = self.pn532.read_passive_target(timeout=0.5)
                if uid is not None:
                    self.handle_card(uid)
                    self.last_scan_time = time.time()
                else:
                    # auto off after 300s (5 menit) - sesuai kebutuhan
                    if (time.time() - self.last_scan_time) > 300:
                        set_brightness(0)
                time.sleep(0.01)
            except Exception as e:
                print("RFID loop error:", e)
                time.sleep(1)

    def handle_card(self, uid: bytes):
        try:
            uid_hex = uid.hex().upper()
            uid_dec = uid_to_decimal(uid)
            print(f"Card detected — HEX: {uid_hex} DEC: {uid_dec}")

            # Set brightness on (contoh 255 atau 16 sesuai yang kamu mau)
            set_brightness(255)

            # Capture photo
            image_path = os.path.join(CAPTURE_DIR, f"{uid_dec}_{int(time.time())}.jpg")
            try:
                self.camera.capture(image_path)
                print("Captured:", image_path)
            except Exception as e:
                print("Camera capture error:", e)
                set_led_mode("FAIL")
                return

            # Upload
            res = upload_image(image_path, uid_hex, uid_dec)
            print("Upload response:", res)

            # set LED based on response
            try:
                # jika server mengembalikan status sukses (contoh kunci "success" atau status code),
                # adjust sesuai response API sebenarnya
                if isinstance(res, dict) and (res.get("success") is True or res.get("status") == "ok"):
                    set_led_mode("OK")
                else:
                    set_led_mode("OK")  # jika API 200 tapi format lain, tetap OK
            except Exception:
                set_led_mode("OK")
        except Exception as e:
            print("handle_card error:", e)
            set_led_mode("FAIL")

    def stop(self):
        self.running = False
        try:
            self.camera.stop()
        except Exception:
            pass
        print("RFID Worker stopped")
