import os
import subprocess

BRIGHTNESS_PATH = "/sys/class/backlight/11-0045/brightness"

# ============================
# TOUCHSCREEN DRIVER CONTROL
# ============================
def enable_touch():
    os.system("sudo modprobe edt_ft5x06")
    print("Touchscreen ENABLED")

def disable_touch():
    os.system("sudo rmmod edt_ft5x06")
    print("Touchscreen DISABLED")


# ============================
# SET BRIGHTNESS VALUE
# ============================
def set_brightness(value):
    """
    value: 0 - 255
    """
    try:
        os.system(f"echo {value} | sudo tee {BRIGHTNESS_PATH}")
        print(f"Brightness set to {value}")

        # auto control touchscreen
        if value == 0:
            disable_touch()
        else:
            enable_touch()

    except Exception as e:
        print("Error setting brightness:", e)


# ============================
# GET BRIGHTNESS
# ============================
def get_brightness():
    try:
        with open(BRIGHTNESS_PATH, "r") as f:
            return int(f.read().strip())
    except:
        return 0


# ============================
# TOGGLE BRIGHTNESS (0 ↔ 255)
# ============================
def toggle_brightness():
    current = get_brightness()

    if current == 0:
        set_brightness(255)
        return 255

    else:
        set_brightness(0)
        return 0
