import time
import os
import RPi.GPIO as GPIO

from config import API_URL, DEVICE_NAME, APP_VERSION
from modules.led import init_led, start_led_thread, set_led_mode
from modules.brightness import set_brightness, auto_brightness_control, BUTTON_PIN, start_button_thread
from modules.camera import init_camera, capture_image_file
from modules.rfid import init_pn532, read_card
from modules.uploader import upload_data
from modules.utils import RUNNING, stop_all
from modules.web import start_web_server



def main():

    print("Starting ATTENDANCE SYSTEM", APP_VERSION)

    # Init LED Thread
    init_led(5)   # atau LED_PIN lain
    start_led_thread()

    # Init brightness + button handler
    set_brightness(255)
    start_button_thread()

    #start web
    start_web_server()


    # Init camera
    picam2 = init_camera()

    # Init RFID
    pn532 = init_pn532()

    last_scan = time.time()
    AUTO_OFF_SECONDS = 300

    print("Tempelkan kartu...")

    while RUNNING:

        # Auto Off brightness
        auto_brightness_control(last_scan, AUTO_OFF_SECONDS)

        # Read RFID
        uid = read_card(pn532)
        if uid is None:
            continue

        # Turn ON brightness when card detected
        set_brightness(255)
        last_scan = time.time()

        print("Reading Card:", uid)

        # Take picture
        img_path = capture_image_file(picam2)
        if img_path is None:
            set_led_mode("FAIL")
            continue

        # Upload to server
        response = upload_data(img_path, uid)

        # Process response
        if response is None:
            set_led_mode("FAIL")
        else:
            status, data_json = response

            if status == 200:
                set_led_mode("OK")
                print(data_json.get("name"))
                print(data_json.get("time"))
            elif status == 404:
                set_led_mode("FAIL")
                print("RFID card not found")
            else:
                set_led_mode("FAIL")
                print("Error:", data_json)

        time.sleep(2)

    stop_all(picam2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApp dihentikan oleh user")
        stop_all()
