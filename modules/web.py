from flask import Flask, render_template
import threading

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def start_web():
    t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True)
    t.start()
