import os
import requests

class Uploader:
    def __init__(self, api_url):
        self.api_url = api_url

    def upload(self, card_number, img_path, device_name):
        try:
            with open(img_path, "rb") as file:
                files = {"leave_letter": ("image.jpg", file, "image/jpeg")}
                data = {"device_name": device_name, "card_number": card_number}
                response = requests.post(self.api_url, data=data, files=files, timeout=15)
            os.remove(img_path)
            return response.status_code, response.json()

        except Exception as e:
            print("Upload gagal:", e)
            try:
                os.remove(img_path)
            except:
                pass
            return None, None
