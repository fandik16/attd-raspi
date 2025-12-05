import threading
import time
import os

from config import API_URL, DEVICE_NAME, APP_VERSION, AUTO_OFF_SECONDS
from modules.utils import RUNNING, LAST_SCAN, uid_to_decimal
from modules.led import led_worker, LED_MODE
from modules.brightness import set_brightness, BRIGHTNESS_IS_ON
from modules.rfid import init_rfid, scan_rfid
from modules.camera import capture_image, stop_camera
from modules.uploader import upload_to_server
from modules.web import start_web

import RPi.GPIO as GPIO


# BUTTON SETUP
BUTTON_PIN = 6
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def button_worker():
    global LAST_SCAN, BRIGHTNESS_IS_ON, RUNNING

    while RUNNING:
        try:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.15)

                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    if BRIGHTNESS_IS_ON:
                        set_brightness(0)
                    else:
                        set_brightness(255)

                    LAST_SCAN = time.time()
                    time.sleep(0.5)

        except:
            break

        time.sleep(0.02)


if __name__ == "__main__":
    print("Starting ATTENDANCE SYSTEM", APP_VERSION)

    # start web server
    start_web()

    # start threads
    threading.Thread(target=led_worker, daemon=True).start()
    threading.Thread(target=button_worker, daemon=True).start()

    # init rfid
    pn532 = init_rfid()

    # brightness on startup
    set_brightness(255)

    try:

        while True:

            # AUTO OFF
            if BRIGHTNESS_IS_ON and (time.time() - LAST_SCAN >= AUTO_OFF_SECONDS):
                set_brightness(0)
                print("Brightness OFF auto")

            uid = scan_rfid(pn532)
            if uid is None:
                continue

            set_brightness(255)
            LAST_SCAN = time.time()

            card_decimal = uid_to_decimal(uid)
            print("CARD:", card_decimal)

            img_path = capture_image()
            if not img_path:
                LED_MODE = "FAIL"
                continue

            resp = upload_to_server(API_URL, DEVICE_NAME, card_decimal, img_path)

            if not resp:
                LED_MODE = "FAIL"
                continue

            if resp.status_code == 200:
                LED_MODE = "OK"
                print(resp.json())
            else:
                LED_MODE = "FAIL"
                print("Server Err:", resp.status_code)

            time.sleep(2)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        RUNNING = False
        time.sleep(0.3)
        GPIO.cleanup()
        stop_camera()
        print("GPIO & Camera Cleaned")
