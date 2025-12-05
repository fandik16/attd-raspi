import os

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
# RAW BRIGHTNESS FUNCTION
# ============================
def set_brightness(value):
    try:
        os.system(f"echo {value} | sudo tee {BRIGHTNESS_PATH}")

        if value == 0:
            disable_touch()
        else:
            enable_touch()

        print(f"Brightness set to {value}")

    except Exception as e:
        print("Brightness Error:", e)


def get_brightness():
    try:
        with open(BRIGHTNESS_PATH, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def toggle_brightness():
    current = get_brightness()
    if current == 0:
        set_brightness(255)
        return 255
    else:
        set_brightness(0)
        return 0


# ============================
# CLASS UNTUK DIPAKAI DI web_app.py
# ============================
class BrightnessControl:
    @staticmethod
    def set(value):
        set_brightness(value)

    @staticmethod
    def get():
        return get_brightness()

    @staticmethod
    def toggle():
        return toggle_brightness()
