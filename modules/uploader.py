import requests

def upload_to_server(api_url, device_name, card_decimal, image_path):
    try:
        with open(image_path, "rb") as f:
            files = {"leave_letter": ("image.jpg", f, "image/jpeg")}
            data = {"device_name": device_name, "card_number": card_decimal}

            return requests.post(api_url, data=data, files=files, timeout=15)

    except Exception as e:
        print("Upload error:", e)
        return None
