import time
import threading
from pn532 import *
from .camera import WebCamera
from .brightness import set_brightness
from .uploader import upload_image
from .utils import uid_to_decimal


class RFIDWorker:
    def __init__(self):
        # PN532 via SPI
        self.pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = self.pn532.get_firmware_version()
        print(f"PN532 Connected — Firmware: {ver}.{rev}")

        self.pn532.SAM_configuration()

        # Kamera hanya dibuat saat class dibuat, TIDAK saat import module
        self.camera = WebCamera()

        self.last_scan_time = time.time()
        self.running = True

    def start(self):
        """Start RFID scanning in background thread."""
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print("RFID Worker Started.")

    def _loop(self):
        """Worker loop."""
        while self.running:
            try:
                uid = self.pn532.read_passive_target(timeout=0.5)

                if uid is not None:
                    self.handle_card(uid)
                    self.last_scan_time = time.time()
                else:
                    # Jika tidak ada kartu selama 60 detik → brightness 0
                    if (time.time() - self.last_scan_time) > 60:
                        set_brightness(0)

            except Exception as e:
                print(f"RFID Error: {e}")
                time.sleep(1)

    def handle_card(self, uid):
        """Called when a card is detected."""
        uid_hex = uid.hex().upper()
        uid_dec = uid_to_decimal(uid)

        print(f"UID HEX: {uid_hex}")
        print(f"UID DEC: {uid_dec}")

        # Nyalakan LCD
        set_brightness(16)

        # Capture foto
        image_path = f"/home/fandik/attd/captures/{uid_dec}.jpg"
        try:
            self.camera.capture(image_path)
            print(f"Captured: {image_path}")
        except Exception as e:
            print(f"Camera Capture Error: {e}")
            return

        # Upload foto
        try:
            upload_result = upload_image(image_path, uid_dec)
            print("Upload Result:", upload_result)
        except Exception as e:
            print("Upload Error:", e)

    def stop(self):
        """Stop worker."""
        self.running = False
        self.camera.st
