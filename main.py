# main.py
import time
import threading # Diperlukan untuk menjalankan Flask secara paralel
import RPi.GPIO as GPIO
from config import API_URL, DEVICE_NAME, APP_VERSION

# PERUBAHAN: Impor modul dashboard
import module.hardware as hardware
import module.nfc as nfc
import module.api_client as api_client
import module.dashboard as dashboard # <-- Import dashboard

# =========================
# FUNGSI THREADING UNTUK DASHBOARD
# =========================
def start_dashboard():
    """Fungsi target untuk thread Flask."""
    dashboard.run_dashboard(DEVICE_NAME, APP_VERSION)

# =========================
# MAIN PROGRAM
# =========================
if __name__ == '__main__':
    try:
        # 1. Inisialisasi dan Start Dashboard (di Thread terpisah)
        print("Starting Flask Dashboard (http://0.0.0.0:5000)...")
        dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
        dashboard_thread.start()
        
        # 2. Inisialisasi Hardware
        hardware.setup_camera()
        hardware.start_led_worker()
        hardware.start_button_worker()
        
        # 3. Inisialisasi NFC Reader
        if not nfc.setup_pn532():
            print("Gagal inisialisasi PN532. Keluar.")
            dashboard.update_status("current_status", "Failed to initialize NFC Reader")
            hardware.cleanup_hardware()
            exit(1)

        print("Application Version", APP_VERSION)
        print("Tempelkan kartu...")
        dashboard.update_status("current_status", "Ready. Waiting for card scan...")

        while hardware.RUNNING:

            # === Auto Off Brightness ===
            hardware.handle_auto_off()

            # === Scan kartu ===
            uid = nfc.scan_card()

            if uid is None:
                # Update status LED di dashboard (meskipun LED_MODE di-update di hardware.py)
                dashboard.update_status("led_mode", hardware.LED_MODE)
                continue

            # === Kartu ditemukan ===
            hardware.set_brightness(255)
            hardware.update_last_scan_time()
            dashboard.update_status("current_status", "Card detected. Capturing image...")


            card_decimal = nfc.uid_to_decimal(uid)
            print("Reading Card:", card_decimal)

            # === Ambil foto ===
            img_path = hardware.capture_image_file()
            if img_path is None:
                hardware.set_led_mode("FAIL")
                dashboard.update_status("current_status", "FAIL: Image capture failed.")
                continue
            
            dashboard.update_status("current_status", "Uploading data...")

            # === Upload ke server ===
            status, data_json = api_client.upload_data(DEVICE_NAME, card_decimal, img_path)

            print("Status:", status)

            # === PROCESS RESPONSE ===
            if status is None or data_json is None:
                hardware.set_led_mode("FAIL")
                dashboard.update_status("current_status", "FAIL: Network/API error.")
                time.sleep(2)
                continue

            if status == 200:
                hardware.set_led_mode("OK")
                
                name = data_json.get("name", "N/A")
                time_rec = data_json.get("time", "N/A")

                dashboard.update_status("last_card_scan", card_decimal)
                dashboard.update_status("last_name", name)
                dashboard.update_status("last_scan_time", time_rec)
                dashboard.update_status("current_status", f"SUCCESS: Logged in as {name}")
                
                print(f"Nama: {name}")
                print(f"Waktu: {time_rec}")

            elif status == 404:
                hardware.set_led_mode("FAIL")
                dashboard.update_status("current_status", "FAIL: RFID card not found (404)")
                print("RFID card not found")

            else:
                hardware.set_led_mode("FAIL")
                dashboard.update_status("current_status", f"FAIL: Server error ({status})")
                print("Error:", data_json)
            
            dashboard.update_status("led_mode", hardware.LED_MODE) # Update mode LED terakhir
            time.sleep(2)
            dashboard.update_status("current_status", "Ready. Waiting for card scan...")


    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")

    finally:
        hardware.cleanup_hardware()
        print("Flask server will shut down shortly.")