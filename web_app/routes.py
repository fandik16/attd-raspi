# web_app/routes.py
from flask import render_template, Response
from modules.camera import WebCamera
from modules.brightness import BrightnessControl
from modules.utils import TouchscreenControl

camera = WebCamera()
brightness = BrightnessControl()
touch = TouchscreenControl()

def init_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    def mjpeg_stream():
        while True:
            frame = camera.get_frame_jpeg()
            if frame:
                yield (b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

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
