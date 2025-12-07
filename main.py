# main.py

import threading
import time
import RPi.GPIO as GPIO
import sys
import os

# Tambahkan direktori module ke path system agar impor berfungsi
sys.path.append(os.path.join(os.path.dirname(__file__), 'module'))

# Import modul
import module.hardware as hardware
import module.nfc as nfc
import module.dashboard as dashboard

# =========================
# STATE MANAGER GLOBAL
# =========================
class StateManager:
    """Kelas untuk mengelola semua state yang dapat diubah di seluruh thread."""
    def __init__(self):
        self.RUNNING = True
        self.LED_MODE = "IDLE"
        self.LAST_SCAN_RESULT = {"name": "N/A", "time": "N/A"}
        self.LAST_SCAN = time.time()
        self.GLOBAL_SETTINGS = self._load_initial_settings()

    def _load_initial_settings(self):
        # Muat settings dari JSON menggunakan fungsi yang ada di dashboard.py
        initial_settings = dashboard.load_settings()
        if not initial_settings:
            return {"API_URL": "N/A", "DEVICE_NAME": "N/A", "AUTO_OFF_SECONDS": 300}
        return initial_settings

# Inisialisasi State Manager
state_manager = StateManager()

# TENTUKAN PROJECT ROOT PATH (Lokasi folder utama)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Inisialisasi Flask App dengan project root path yang benar
app = dashboard.create_app(state_manager, hardware, PROJECT_ROOT)

# =========================
# MAIN EXECUTION
# =========================
if __name__ == '__main__': # <-- Baris 47
    
    # 1. Mulai Kamera
    hardware.start_camera() # <-- Baris ini harus diindentasi dengan benar
    
    # 2. Mulai Worker Threads
    
    # Worker LED
    threading.Thread(target=hardware.led_worker, args=(state_manager,), daemon=True).start()
    
    # Worker Tombol Brightness
    threading.Thread(target=hardware.button_worker, args=(state_manager,), daemon=True).start()
    
    # Worker NFC & API Utama
    threading.Thread(target=nfc.nfc_worker, args=(state_manager,), daemon=True).start()

    print("All workers started. Running application...")
    
    try:
        # 3. Jalankan Flask Server
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