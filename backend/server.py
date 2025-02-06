from flask import Flask
from flask_socketio import SocketIO
from threading import Thread
from pymavlink import mavutil
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MAVLink setup
serial_port = "COM5"  # Update this if your port is different
baud_rate = 57600

# Establish MAVLink connection
master = mavutil.mavlink_connection(serial_port, baud=baud_rate)

# Request telemetry data
master.mav.request_data_stream_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 2, 1
)

# Persistent telemetry data dictionary
telemetry_data = {
    "latitude": 0,  # Default values
    "longitude": 0,
    "altitude": 0.0,
    "speed": 0.0,
    "heading": 0,
    "battery": 100,
    "satellites": 0
}

@app.route("/")
def home():
    return "WebSocket Server Running"

@socketio.on("connect")
def handle_connect():
    print("✅ [WebSocket Server] Client connected!")
    # Send initial data on connection
    socketio.emit("droneData", telemetry_data)

def start_telemetry():
    """Runs telemetry reading in a separate thread."""
    while True:
        try:
            # Read all available messages in the queue
            while True:
                msg = master.recv_match(blocking=False)
                if msg is None:
                    break  # No more messages in queue
                
                msg_type = msg.get_type()

                # Update only if new values are received, keeping old values otherwise
                if msg_type == "GLOBAL_POSITION_INT":
                    if msg.lat: telemetry_data["latitude"] = msg.lat / 1e7
                    if msg.lon: telemetry_data["longitude"] = msg.lon / 1e7
                    if msg.relative_alt: telemetry_data["altitude"] = msg.relative_alt / 1000

                elif msg_type == "VFR_HUD":
                    if hasattr(msg, 'groundspeed'): telemetry_data["speed"] = msg.groundspeed
                    if hasattr(msg, 'heading'): telemetry_data["heading"] = msg.heading

                elif msg_type == "SYS_STATUS":
                    if hasattr(msg, 'battery_remaining'): telemetry_data["battery"] = msg.battery_remaining

                elif msg_type == "GPS_RAW_INT":
                    if hasattr(msg, 'satellites_visible'): telemetry_data["satellites"] = msg.satellites_visible

            # Emit the latest data after processing all messages
            print(f"📡 [Server] Sending to WebSocket: {telemetry_data}")
            socketio.emit("droneData", telemetry_data)
            
        except Exception as e:
            print(f"Error reading telemetry: {e}")
        
        time.sleep(2)  # Wait for 2 seconds before next batch

if __name__ == "__main__":
    print("🚀 Starting WebSocket Server...")
    
    telemetry_thread = Thread(target=start_telemetry, daemon=True)
    telemetry_thread.start()
    
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)