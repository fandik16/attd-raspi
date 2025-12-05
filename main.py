# main.py
import threading
from web_app import app
from modules.rfid import RFIDWorker
from modules.led import led_worker
from modules.utils import ButtonWatcher

if __name__ == "__main__":
    # LED Thread
    threading.Thread(target=led_worker, daemon=True).start()

    # RFID Thread
    rfid = RFIDWorker()
    threading.Thread(target=rfid.run, daemon=True).start()

    # Button Thread
    button = ButtonWatcher()
    threading.Thread(target=button.run, daemon=True).start()

    print("System Running → http://0.0.0.0:5000")

    app.run(host="0.0.0.0", port=5000, threaded=True)
