def uid_to_decimal(uid):
    hex_str = ''.join(f"{x:02x}" for x in reversed(uid))
    return str(int(hex_str, 16)).zfill(10)
