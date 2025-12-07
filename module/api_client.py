# module/api_client.py

import requests
import os

def upload_attendance(img_path, card_decimal, device_name, api_url):
    """Mengirim data absensi dan gambar ke API server."""
    
    if not api_url or api_url == 'N/A':
        print("API_URL tidak valid. Melewati upload.")
        return {"error": "API URL not configured"}, None

    try:
        with open(img_path, "rb") as img_file:
            files = {"leave_letter": ("image.jpg", img_file, "image/jpeg")}
            data = {"device_name": device_name, "card_number": card_decimal}
            
            response = requests.post(api_url, data=data, files=files, timeout=15)
            status = response.status_code
            
            try:
                response_data = response.json()
            except:
                print("Server response bukan JSON.")
                response_data = {"error": "Invalid JSON response"}
            
            return response_data, status

    except requests.exceptions.Timeout:
        print("Gagal upload: Timeout.")
        return {"error": "Upload Timeout"}, None
    except requests.exceptions.RequestException as e:
        print(f"Gagal upload: {e}")
        return {"error": str(e)}, None
    except Exception as e:
        print(f"Kesalahan tak terduga saat upload: {e}")
        return {"error": "Unknown upload error"}, None