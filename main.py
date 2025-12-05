import time
from modules.led import LEDController
from modules.brightness import BrightnessController
from modules.camera import Camera
from modules.rfid import RFIDReader
from modules.uploader import Uploader
from config import API_URL, DEVICE_NAME, APP_VERSION

def main():
    print("Application Version", APP_VERSION)

    led = LEDController()
    brightness = BrightnessController()
    camera = Camera()
    rfid = RFIDReader()
    uploader = Uploader(API_URL)

    print("Tempelkan kartu...")

    try:
        while True:
            brightness.auto_off_check()

            uid = rfid.read_card()
            if uid is None:
                continue

            brightness.turn_on()
            card_decimal = rfid.uid_to_decimal(uid)
            print("Reading Card:", card_decimal)

            img_path = camera.capture_image()
            if img_path is None:
                led.fail()
                continue

            status, data_json = uploader.upload(card_decimal, img_path, DEVICE_NAME)
            print("Status:", status)

            if status == 200:
                led.ok()
                print(data_json.get("name"))
                print(data_json.get("time"))

            elif status == 404:
                led.fail()
                print("RFID card not found")

            else:
                led.fail()
                print("Error:", data_json)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")

if __name__ == "__main__":
    main()
