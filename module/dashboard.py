# module/dashboard.py

from flask import Flask, render_template, Response, request, redirect, url_for, flash
import time
import json
import os
import tempfile
import cv2

# Import dari konfigurasi
from config import APP_VERSION, SETTINGS_PASSWORD, SETTINGS_FILE
from . import hardware # Digunakan untuk streaming kamera

# =========================
# FUNGSI MANAJEMEN KONFIGURASI JSON
# =========================

def load_settings():
    """Memuat pengaturan dari file JSON."""
    try:
        if not os.path.exists(SETTINGS_FILE):
            return {}
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings_safely(data):
    """Menyimpan pengaturan ke file JSON menggunakan penulisan atomik yang aman."""
    tmp_path = None
    try:
        # ... (kode penulisan ke file sementara) ...
        tmp_path = tmp_file.name
        os.replace(tmp_path, SETTINGS_FILE)
        return True
    except Exception as e:
        # Tampilkan error di terminal saat terjadi kegagalan
        print(f"!!! FILE I/O ERROR: Gagal menulis settings.json: {e}") 
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False # Mengembalikan False, memicu flash message

# =========================
# FLASK APP INITIALIZATION & ROUTES
# =========================
def create_app(state_manager, hardware_module, root_path):
    
    # INI ADALAH PERBAIKAN UTAMA: Menggunakan root_path untuk menunjukkan lokasi folder 'templates'
    app = Flask(__name__, root_path=root_path) 
    app.secret_key = 'supersecretkey'

    @app.route('/')
    def index():
        error = request.args.get('error')
        return render_template('index.html', error=error)

    @app.route('/settings/verify', methods=['POST'])
    def verify_settings():
        password = request.form.get('password')
        if password == SETTINGS_PASSWORD:
            return redirect(url_for('settings'))
        else:
            return redirect(url_for('index', error='password_fail'))

    @app.route('/settings')
    def settings():
        settings_data = load_settings() 
        return render_template('settings.html', 
                               api_url=settings_data.get('API_URL'), 
                               device_name=settings_data.get('DEVICE_NAME'))

    @app.route('/save_settings', methods=['POST'])
    def save_settings():
        new_api_url = request.form.get('api_url')
        new_device_name = request.form.get('device_name')

        current_settings = load_settings()
        
        current_settings["API_URL"] = new_api_url
        current_settings["DEVICE_NAME"] = new_device_name

        if save_settings_safely(current_settings):
            state_manager.GLOBAL_SETTINGS = current_settings
            
            flash('Pengaturan berhasil disimpan. Harap restart aplikasi untuk menerapkan perubahan pada seluruh sistem.', 'success')
        else:
            flash('Gagal menyimpan pengaturan.', 'danger')
            
        return redirect(url_for('settings'))

    # Stream video ke web
    def generate_frames():
        while True:
            try:
                frame = hardware_module.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception:
                time.sleep(0.1)
                continue

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/api/status')
    def api_status():
        return {
            "app_version": APP_VERSION,
            "server_time": time.strftime("%H:%M:%S", time.localtime()),
            "current_status": "Ready. Waiting for card scan...",
            "led_mode": state_manager.LED_MODE,
            "last_name": state_manager.LAST_SCAN_RESULT["name"],
            "last_scan_time": state_manager.LAST_SCAN_RESULT["time"]
        }

    return app