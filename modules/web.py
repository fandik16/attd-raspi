from flask import Flask, render_template, jsonify, request
import threading

from modules.led import get_led_mode, set_led_mode
from modules.brightness import get_brightness, set_brightness
from modules.utils import RUNNING

app = Flask(__name__, template_folder="../templates")

# ============================
# DASHBOARD ROUTES
# ============================

@app.route("/")
def index():
    return render_template("index.html")


# -------- LED API ----------

@app.route("/api/led")
def api_led_status():
    return jsonify({"mode": get_led_mode()})


@app.route("/api/led/set", methods=["POST"])
def api_led_set():
    data = request.json or {}
    mode = data.get("mode")

    try:
        set_led_mode(mode)
        return jsonify({"ok": True, "mode": mode})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# -------- Brightness API ----------

@app.route("/api/brightness")
def api_get_brightness():
    return jsonify({"brightness": get_brightness()})


@app.route("/api/brightness/set", methods=["POST"])
def api_set_brightness():
    data = request.json or {}
    level = data.get("brightness")

    try:
        set_brightness(int(level))
        return jsonify({"ok": True, "brightness": level})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ============================
# DASHBOARD SERVER THREAD
# ============================

def start_web_server():
    """Menjalankan Flask di thread background."""
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, threaded=True),
        daemon=True
    )
    thread.start()
    print("Web dashboard berjalan di http://<raspi-ip>:5000")


