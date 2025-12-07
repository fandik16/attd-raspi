# main.py

import threading
import time
import RPi.GPIO as GPIO
import os
import json
import sys

# Tambahkan direktori module ke path system
sys.path.append(os.path.join(os.path.dirname(__file__), 'module'))

# Import modul
import module.hardware as hardware
import module.nfc as nfc
import module.dashboard as dashboard

# =========================
# STATE MANAGER GLOBAL (Menggantikan variabel global yang tersebar)
# =========================
class StateManager:
    def __init__(self):
        self.RUNNING = True
        self.LED_MODE = "IDLE"
        self.LAST_SCAN_RESULT = {"name": "N/A", "time": "N/A"}
        self.LAST_SCAN = time.time()
        self.GLOBAL_SETTINGS = self._load_initial_settings()

    def _load_initial_settings(self):
        # Menggunakan fungsi load dari dashboard.py (yang menggunakan SETTINGS_FILE)
        initial_settings = dashboard.load_settings()
        if not initial_settings:
            # Jika settings.json kosong, gunakan default minimal
            return {"API_URL": "N/A", "DEVICE_NAME": "N/A", "AUTO_OFF_SECONDS": 300}
        return initial_settings

# Inisialisasi State Manager
state_manager = StateManager()
app = dashboard.create_app(state_manager, hardware)

# =========================
# MAIN EXECUTION
# =========================
if __name__ == '__main__':
    
    # 1. Mulai Kamera
    hardware.start_camera()

    # 2. Mulai Worker Threads
    
    # Worker LED
    threading.Thread(target=hardware.led_worker, args=(state_manager,), daemon=True).start()
    
    # Worker Tombol Brightness
    threading.Thread(target=hardware.button_worker, args=(state_manager,), daemon=True).start()
    
    # Worker NFC & API Utama
    threading.Thread(target=nfc.nfc_worker, args=(state_manager,), daemon=True).start()

    print("All threads initialized.")
    
    try:
        # 3. Jalankan Flask Server
        # Gunakan host 0.0.0.0 agar dapat diakses dari jaringan
        app.run(host='0.0.0.0', port=5000, threaded=True)

    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")

    finally:
        print("Starting cleanup...")
        state_manager.RUNNING = False # Sinyal ke semua thread untuk berhenti
        time.sleep(1) 

        GPIO.cleanup()
        hardware.stop_camera()
        print("Cleanup Complete. Application Exiting.")