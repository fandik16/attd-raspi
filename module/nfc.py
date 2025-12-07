# nfc.py
from pn532 import *
import time

# =========================
# SETUP PN532
# =========================
pn532 = PN532_SPI(debug=False, reset=20, cs=4)

def setup_pn532():
    try:
        pn532.SAM_configuration()
        return True
    except Exception as e:
        print("Gagal konfigurasi PN532:", e)
        return False

def uid_to_decimal(uid):
    """Mengkonversi UID dari format byte ke string desimal 10 digit."""
    try:
        # uid.hex() untuk Python >= 3.10
        hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
        return str(int(hex_str, 16)).zfill(10)
    except Exception:
        return "0000000000"

def scan_card():
    """Mencoba membaca UID dari kartu NFC."""
    try:
        uid = pn532.read_passive_target(timeout=0.5)
        return uid
    except Exception:
        print("PN532 error: retrying...")
        time.sleep(0.5)
        return None