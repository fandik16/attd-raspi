import requests
import os
from config import API_URL, DEVICE_NAME


def upload_data(img_path, uid):

    try:
        with open(img_path, "rb") as img:
            files = {"leave_letter": ("image.jpg", img, "image/jpeg")}
            data = {"device_name": DEVICE_NAME, "card_number": uid}

            resp = requests.post(API_URL, data=data, files=files, timeout=15)
            status = resp.status_code

    except Exception as e:
        print("Gagal upload:", e)
        status = None
        resp = None

    finally:
        try:
            os.remove(img_path)
        except:
            pass

    if resp is None:
        return None

    try:
        data_json = resp.json()
    except:
        print("Response bukan JSON!")
        return None

    return status, data_json
