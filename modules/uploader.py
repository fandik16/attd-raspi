# modules/uploader.py
import requests
import os
import time

# IMPORT CONFIG DARI PARENT FOLDER (tempat main.py)
from config import API_URL, DEVICE_NAME


def upload_image(image_path: str, uid_hex: str, uid_dec: int):
    """
    Upload foto + UID ke API attendance-logs.
    """

    if not os.path.exists(image_path):
        return {
            "success": False,
            "message": f"File foto tidak ditemukan: {image_path}"
        }

    try:
        with open(image_path, "rb") as f:
            files = {
                "photo": (os.path.basename(image_path), f, "image/jpeg")
            }

            data = {
                "uid_hex": uid_hex,
                "uid_dec": uid_dec,
                "device_name": DEVICE_NAME
            }

            response = requests.post(
                API_URL,
                files=files,
                data=data,
                timeout=15
            )

        try:
            result = response.json()
        except Exception:
            return {
                "success": False,
                "message": "Server mengirim respon non-JSON",
                "raw": response.text
            }

        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"Upload error: {e}"
        }
