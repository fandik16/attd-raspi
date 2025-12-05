from pn532 import *

def init_pn532():
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    try:
        pn532.SAM_configuration()
    except Exception as e:
        print("Gagal konfigurasi PN532:", e)
    return pn532


def uid_to_decimal(uid):
    try:
        h = ''.join(f"{x:02x}" for x in reversed(uid))
        return str(int(h, 16)).zfill(10)
    except:
        return "0000000000"


def read_card(pn532):
    try:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid:
            return uid_to_decimal(uid)
    except:
        print("PN532 error")
    return None
