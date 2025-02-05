import socketio

# Initialize WebSocket client
sio = socketio.Client()

def connect_to_server():
    """Connects to the WebSocket server."""
    try:
        sio.connect("http://localhost:5000")  # Connect to WebSocket server
        print("Connected to WebSocket server!")
    except Exception as e:
        print(f"WebSocket Connection Error: {e}")

def send_telemetry(data):
    """Sends telemetry data to the WebSocket server."""
    if sio.connected:
        sio.emit("droneData", data)
