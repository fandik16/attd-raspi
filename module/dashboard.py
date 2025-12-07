# module/dashboard.py
from flask import Flask, render_template, jsonify
import time

app = Flask(__name__)

# Variabel Global untuk menyimpan status yang akan ditampilkan di web
status_data = {
    "device_name": "",
    "app_version": "",
    "current_status": "Starting up...",
    "last_card_scan": "N/A",
    "last_name": "N/A",
    "last_scan_time": "N/A",
    "led_mode": "IDLE"
}

@app.route('/')
def index():
    """Route utama untuk menampilkan dashboard HTML."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint untuk mengambil data status JSON secara real-time."""
    # Pastikan waktu terakhir diperbarui saat permintaan
    status_data['server_time'] = time.strftime("%H:%M:%S")
    return jsonify(status_data)

def update_status(key, value):
    """Fungsi utilitas untuk memperbarui data status dari main.py."""
    global status_data
    status_data[key] = value

def run_dashboard(device_name, app_version):
    """Menjalankan server Flask."""
    global status_data
    status_data['device_name'] = device_name
    status_data['app_version'] = app_version
    # Menjalankan Flask di background
    app.run(host='0.0.0.0', port=5000, debug=False)