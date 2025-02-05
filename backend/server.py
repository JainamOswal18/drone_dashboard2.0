from flask import Flask
from flask_socketio import SocketIO
from utils.telemetry_handler import TelemetryHandler
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("droneData")
def handle_drone_data(data):
    print(f"Received Data: {data}")
    socketio.emit("droneData", data)

@app.route("/")
def home():
    return "WebSocket Server Running"

def start_telemetry():
    """Runs telemetry in real or simulation mode"""
    telemetry = TelemetryHandler(serial_port=None)  # Set to None for simulation
    telemetry.start_reading()

if __name__ == "__main__":
    threading.Thread(target=start_telemetry, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
