# module/nfc.py

from pn532 import *
import time
import tempfile
import cv2
import os
from . import api_client
from . import hardware

# =========================
# Utility
# =========================
def uid_to_decimal(uid):
    """Konversi UID byte ke string desimal."""
    try:
        hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
        return str(int(hex_str, 16)).zfill(10)
    except Exception:
        return "0000000000"

# =========================
# NFC Worker
# =========================
def nfc_worker(state_manager):
    """Worker utama yang memproses pembacaan NFC, kamera, dan API."""
    
    # Inisialisasi PN532 di dalam worker
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        pn532.SAM_configuration()
    except Exception as e:
        print(f"Gagal konfigurasi PN532: {e}. NFC Worker dimatikan.")
        return 

    print("RFID Worker Started. Tempelkan kartu...")

    while state_manager.RUNNING:
        try:
            # === Auto Off ===
            auto_off = state_manager.GLOBAL_SETTINGS.get('AUTO_OFF_SECONDS', 300)
            if hardware.BRIGHTNESS_IS_ON and (time.time() - state_manager.LAST_SCAN >= auto_off):
                hardware.set_brightness(0)
                print("Brightness OFF (auto)")

            # === Scan kartu ===
            uid = pn532.read_passive_target(timeout=0.5)

            if uid is None:
                continue

            # === Kartu ditemukan ===
            hardware.set_brightness(255)
            state_manager.LAST_SCAN = time.time()

            card_decimal = uid_to_decimal(uid)
            print("Reading Card:", card_decimal)

            # === Ambil foto dan simpan sementara ===
            frame = hardware.capture_image_array()
            if frame is None:
                state_manager.LED_MODE = "FAIL"
                continue
            
            img_path = None
            try:
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                cv2.imwrite(temp.name, frame)
                img_path = temp.name
            except Exception as e:
                print(f"Gagal menyimpan gambar sementara: {e}")
                state_manager.LED_MODE = "FAIL"
                continue

            # === Upload ke server ===
            response_data, status_code = api_client.upload_attendance(
                img_path, 
                card_decimal,
                state_manager.GLOBAL_SETTINGS.get('DEVICE_NAME'),
                state_manager.GLOBAL_SETTINGS.get('API_URL')
            )

            # Bersihkan file sementara
            if os.path.exists(img_path):
                os.remove(img_path)

            # === PROCESS RESPONSE (PERBAIKAN DI SINI) ===
            if status_code is None:
                error_msg = "Upload Error (Timeout/Network)"
                state_manager.LED_MODE = "FAIL"
            elif status_code == 200:
                error_msg = response_data.get("name", "SUCCESS")
                state_manager.LED_MODE = "OK"
            elif status_code == 404:
                # Menampilkan "message" jika ada, jika tidak, gunakan default.
                error_msg = response_data.get("message", "Card Not Found")
                state_manager.LED_MODE = "FAIL"
            else:
                error_msg = f"Server Error {status_code}"
                state_manager.LED_MODE = "FAIL"

            state_manager.LAST_SCAN_RESULT["name"] = error_msg
            state_manager.LAST_SCAN_RESULT["time"] = time.strftime("%H:%M:%S")

            time.sleep(2)

        except Exception as e:
            print(f"NFC Worker Error: {e}")
            time.sleep(5)