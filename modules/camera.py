from picamera2 import Picamera2
from datetime import datetime
import os

class WebCamera:
    def __init__(self):
        self.picam = None

    def start(self):
        if self.picam is None:
            self.picam = Picamera2()
            config = self.picam.create_still_configuration()
            self.picam.configure(config)
            self.picam.start()

    def capture(self, path):
        self.start()
        self.picam.capture_file(path)
        return path

    def stop(self):
        if self.picam:
            self.picam.stop()
            self.picam.close()
            self.picam = None
