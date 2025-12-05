import time

def uid_to_decimal(uid):
    try:
        hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
        return str(int(hex_str, 16)).zfill(10)
    except:
        return "0000000000"

RUNNING = True
LAST_SCAN = time.time()
