import requests
import os

def upload_data(api_url, device_name, card_number, img_path):
    with open(img_path, "rb") as f:
        files = {
            "leave_letter": ("image.jpg", f, "image/jpeg")
        }
        data = {
            "device_name": device_name,
            "card_number": card_number
        }
        return requests.post(api_url, data=data, files=files)
