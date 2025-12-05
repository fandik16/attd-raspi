# web_app.py
from flask import Flask, Response, render_template
from modules.camera import WebCamera
from modules.brightness import BrightnessControl
from modules.utils import TouchControl

app = Flask(__name__)

camera = WebCamera(size=(1280, 720))
brightness = BrightnessControl()
touch = TouchControl()

camera.start()


def mjpeg_stream():
    while True:
        frame = camera.get_frame_jpeg()
        if frame:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(mjpeg_stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/brightness/<int:value>")
def set_brightness(value):
    brightness.set(value)

    if value == 0:
        touch.disable()
    else:
        touch.enable()

    return f"Brightness={value}"
