from pn532 import *

def init_rfid():
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    pn532.SAM_configuration()
    return pn532


def read_card(pn532):
    return pn532.read_passive_target(timeout=0.5)
