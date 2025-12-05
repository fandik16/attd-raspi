# modules/uploader.py
import requests
import os

class Uploader:
    def send(self, url, device_name, card_number, img_path):
        try:
            with open(img_path, "rb") as img:
                files = {"leave_letter": ("image.jpg", img, "image/jpeg")}
                data = {"device_name": device_name, "card_number": card_number}
                return requests.post(url, data=data, files=files)
        except Exception as e:
            print("Upload Error:", e)
            return None
