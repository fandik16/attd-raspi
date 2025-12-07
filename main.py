# main.py
import time
import RPi.GPIO as GPIO
from config import API_URL, DEVICE_NAME, APP_VERSION

# PERUBAHAN: Impor dari paket 'module'
import module.hardware as hardware
import module.nfc as nfc
import module.api_client as api_client

# =========================
# MAIN PROGRAM
# (Isi program tidak berubah, hanya cara impornya)
# =========================
if __name__ == '__main__':
    try:
        # Inisialisasi Hardware
        hardware.setup_camera()
        hardware.start_led_worker()
        hardware.start_button_worker()
        
        # Inisialisasi NFC Reader
        if not nfc.setup_pn532():
            print("Gagal inisialisasi PN532. Keluar.")
            hardware.cleanup_hardware()
            exit(1)

        print("Application Version", APP_VERSION)
        print("Tempelkan kartu...")

        while hardware.RUNNING:

            # === Auto Off Brightness ===
            hardware.handle_auto_off()

            # === Scan kartu ===
            uid = nfc.scan_card()

            if uid is None:
                continue

            # === Kartu ditemukan ===
            hardware.set_brightness(255)
            hardware.update_last_scan_time()

            card_decimal = nfc.uid_to_decimal(uid)
            print("Reading Card:", card_decimal)

            # === Ambil foto ===
            img_path = hardware.capture_image_file()
            if img_path is None:
                hardware.set_led_mode("FAIL")
                continue

            # === Upload ke server ===
            # Tidak perlu mengubah baris ini, karena variabel DEVICE_NAME dan card_decimal sudah ada
            status, data_json = api_client.upload_data(DEVICE_NAME, card_decimal, img_path)

            print("Status:", status)

            # === PROCESS RESPONSE ===
            if status is None or data_json is None:
                hardware.set_led_mode("FAIL")
                time.sleep(2)
                continue

            if status == 200:
                hardware.set_led_mode("OK")
                print(f"Nama: {data_json.get('name')}")
                print(f"Waktu: {data_json.get('time')}")

            elif status == 404:
                hardware.set_led_mode("FAIL")
                print("RFID card not found")

            else:
                hardware.set_led_mode("FAIL")
                print("Error:", data_json)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")

    finally:
        hardware.cleanup_hardware()