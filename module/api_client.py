# module/api_client.py
import requests
import os
from config import API_URL # Tetap sama

def upload_data(device_name, card_decimal, img_path):
    """Mengirim data kartu dan file gambar ke API server."""
    # ... (Isi fungsi tetap sama seperti sebelumnya) ...
    status = None
    response_json = None

    try:
        with open(img_path, "rb") as img_file:
            files = {"leave_letter": ("image.jpg", img_file, "image/jpeg")}
            data = {"device_name": device_name, "card_number": card_decimal}
            
            print(f"Uploading data to {API_URL}...")
            response = requests.post(API_URL, data=data, files=files, timeout=15)
            
            status = response.status_code
            try:
                response_json = response.json()
            except:
                print("Response bukan JSON!")
                return status, None

    except Exception as e:
        print("Gagal upload:", e)
        status = None
        response_json = None
    
    finally:
        try:
            os.remove(img_path)
        except:
            pass

    return status, response_json