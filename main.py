import time
import os
import RPi.GPIO as GPIO

from config import API_URL, DEVICE_NAME, APP_VERSION

from modules.led import start_led_thread, set_led_mode
from modules.camera import capture_image, stop_camera
from modules.rfid import init_rfid, read_card
from modules.uploader import upload_data
from modules.utils import uid_to_decimal
from modules.brightness import (
    brightness_auto_check,
    brightness_on,
    update_last_scan,
    toggle_brightness
)

from modules.button import button_pressed


if __name__ == "__main__":
    try:
        print("Application Version", APP_VERSION)

        # Start LED
        start_led_thread()

        # Brightness ON at boot
        brightness_on()

        # Button listener
        button_pressed(toggle_brightness)

        # Init RFID
        pn532 = init_rfid()
        print("Tempelkan kartu...")

        while True:

            brightness_auto_check()

            # Scan kartu
            uid = read_card(pn532)
            if uid is None:
                continue

            brightness_on()
            update_last_scan()

            card_dec = uid_to_decimal(uid)
            print("Reading Card:", card_dec)

            img_path = capture_image()
            if img_path is None:
                set_led_mode("FAIL")
                continue

            response = upload_data(API_URL, DEVICE_NAME, card_dec, img_path)
            os.remove(img_path)

            print("Status:", response.status_code)

            try:
                js = response.json()
            except:
                print("Response JSON invalid")
                set_led_mode("FAIL")
                continue

            if response.status_code == 200:
                print(js.get("name"))
                print(js.get("time"))
                set_led_mode("OK")

            elif response.status_code == 404:
                print("RFID card not found")
                set_led_mode("FAIL")

            else:
                print("Error:", js)
                set_led_mode("FAIL")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nApp stopped")

    finally:
        GPIO.cleanup()
        stop_camera()
        print("GPIO Clear, Camera Stopped")
