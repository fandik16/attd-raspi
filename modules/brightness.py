# modules/brightness.py
import os

class BrightnessControl:

    PATH = "/sys/class/backlight/11-0045/brightness"

    def set(self, value):
        os.system(f"echo {value} | sudo tee {self.PATH}")

    def get(self):
        try:
            with open(self.PATH, "r") as f:
                return int(f.read().strip())
        except:
            return 0
