from pn532 import *
import time

class RFIDReader:
    def __init__(self):
        self.pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        try:
            self.pn532.SAM_configuration()
        except:
            print("Gagal konfigurasi PN532")

    def read_card(self):
        try:
            return self.pn532.read_passive_target(timeout=0.5)
        except:
            print("PN532 error: retrying...")
            time.sleep(0.5)
            return None

    def uid_to_decimal(self, uid):
        try:
            hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
            return str(int(hex_str, 16)).zfill(10)
        except:
            return "0000000000"
