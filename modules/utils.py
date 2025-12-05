RUNNING = True

def stop_all(cam=None):
    global RUNNING
    RUNNING = False

    import time
    import RPi.GPIO as GPIO
    
    time.sleep(0.2)

    if cam:
        try:
            cam.stop()
        except:
            pass

    GPIO.cleanup()
    print("GPIO Clear, Camera Stopped")
