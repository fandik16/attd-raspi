from flask import Flask, render_template, jsonify, Response
import time
import os
import module.hardware as hardware # Import hardware module untuk akses fungsi kamera

# Mendapatkan jalur root proyek (satu tingkat di atas 'module')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')

# Inisialisasi Flask dengan jalur template yang benar
app = Flask(__name__, template_folder=TEMPLATE_DIR) 

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

@app.route('/video_feed')
def video_feed():
    """Route untuk streaming video MJPEG."""
    # Pastikan server_status di set (MIME type MJPEG)
    return Response(
        generate_frames(), 
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def generate_frames():
    """Fungsi generator yang terus-menerus mengambil frame dan mengirimkannya."""
    while True:
        frame_bytes = hardware.get_jpeg_frame()
        
        if frame_bytes:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )
        time.sleep(0.05) # Jeda kecil untuk mengontrol frame rate

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