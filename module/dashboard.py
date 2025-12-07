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
# Tentukan direktori proyek untuk file sementara
PROJECT_DIR = os.path.dirname(os.path.abspath(SETTINGS_FILE))
# =========================
# FUNGSI MANAJEMEN KONFIGURASI JSON (Diperbaiki untuk Cross-Device Link)
# =========================

# Fungsi load_settings tetap sama
def load_settings():
    """Memuat pengaturan dari file JSON."""
    try:
        if not os.path.exists(SETTINGS_FILE):
            return {}
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"!!! CONFIG ERROR: Gagal memuat {SETTINGS_FILE}: {e}")
        return {}


def save_settings_safely(data):
    """Menyimpan pengaturan ke file JSON menggunakan penulisan atomik yang aman."""
    
    tmp_path = None
    
    try:
        # PERUBAHAN UTAMA: Gunakan 'dir=PROJECT_DIR' untuk membuat file sementara di folder proyek
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=PROJECT_DIR) as tmp_file:
            json.dump(data, tmp_file, indent=4)
        
        tmp_path = tmp_file.name
        
        # os.replace() sekarang berfungsi karena tmp_path dan SETTINGS_FILE berada di File System yang sama
        os.replace(tmp_path, SETTINGS_FILE)
        return True
        
    except Exception as e:
        print(f"!!! FILE I/O ERROR: Gagal menulis {SETTINGS_FILE}: {e}")
        
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            
        return False

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
        # Tentukan persentase pemotongan (misalnya 0.2 = 20% dari setiap sisi akan dipotong)
        CROP_PERCENT = 0.2 
        
        while True:
            try:
                # 1. Ambil Frame Asli
                frame = hardware_module.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                height, width, _ = frame.shape
                
                # 2. Hitung Koordinat Cropping (Digital Zoom)
                start_row = int(height * CROP_PERCENT)
                end_row = int(height * (1 - CROP_PERCENT))
                start_col = int(width * CROP_PERCENT)
                end_col = int(width * (1 - CROP_PERCENT))
                
                # 3. Potong (Zoom In) Frame
                frame_cropped = frame[start_row:end_row, start_col:end_col]
                
                # 4. Putar Frame 90 Derajat (Untuk tampilan vertikal)
                #frame_rotated = cv2.rotate(frame_cropped, cv2.ROTATE_90_CLOCKWISE)

                # 5. Encode dan Stream
                ret, buffer = cv2.imencode('.jpg', frame_rotated)
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