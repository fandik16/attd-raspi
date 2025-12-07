# main.py

import threading
import time
import RPi.GPIO as GPIO
import sys
import os # <-- IMPORT OS

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
# ... (kode StateManager tetap sama) ...
    def __init__(self):
        self.RUNNING = True
        self.LED_MODE = "IDLE"
        self.LAST_SCAN_RESULT = {"name": "N/A", "time": "N/A"}
        self.LAST_SCAN = time.time()
        self.GLOBAL_SETTINGS = self._load_initial_settings()

    def _load_initial_settings(self):
        initial_settings = dashboard.load_settings()
        if not initial_settings:
            return {"API_URL": "N/A", "DEVICE_NAME": "N/A", "AUTO_OFF_SECONDS": 300}
        return initial_settings

# Inisialisasi State Manager
state_manager = StateManager()

# TENTUKAN PROJECT ROOT PATH (Lokasi folder attendance_kiosk/)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Inisialisasi Flask App dengan project root path yang benar
app = dashboard.create_app(state_manager, hardware, PROJECT_ROOT) # <-- PASS PROJECT_ROOT

# =========================
# MAIN EXECUTION
# =========================
if __name__ == '__main__':
# ... (rest of the code remains the same) ...