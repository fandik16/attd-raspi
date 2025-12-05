import RPi.GPIO as GPIO
import time

BUTTON_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def button_pressed(callback):
    """
    Panggil callback() saat tombol ditekan.
    Debounce 300 ms.
    """
    GPIO.add_event_detect(
        BUTTON_PIN,
        GPIO.FALLING,
        callback=lambda channel: callback(),
        bouncetime=300
    )
