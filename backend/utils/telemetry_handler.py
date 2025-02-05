from utils.websocket_handler import send_telemetry
import time

class TelemetryHandler:
    def __init__(self, serial_port=None, baud_rate=57600):
        """If serial_port is None, use simulation mode"""
        self.simulation_mode = serial_port is None
        if not self.simulation_mode:
            from pymavlink import mavutil  # Import only if real telemetry is used
            self.master = mavutil.mavlink_connection(serial_port, baud=baud_rate)
        else:
            print("🚀 Running in Simulation Mode (No Hardware Connected)")

    def start_reading(self):
        """Reads real telemetry if connected, otherwise sends simulated data"""
        while True:
            if self.simulation_mode:
                # Generate Fake Telemetry Data
                telemetry_data = {
                    "latitude": 18.51957,  # Static latitude for Pune, India
                    "longitude": 73.85535,  # Static longitude
                    "altitude": 100 + (time.time() % 10),  # Simulated altitude change
                    "speed": 5,  # Simulated speed
                    "battery": 90,  # Fake battery level
                    "heading": 180,  # Fake heading
                    "satellites": 8,  # Fake satellite count
                    "signalStrength": 80  # Fake signal strength
                }
            else:
                # Read real telemetry from MAVLink
                msg = self.master.recv_match(blocking=True)
                if msg and msg.get_type() == "GLOBAL_POSITION_INT":
                    telemetry_data = {
                        "latitude": msg.lat / 1e7 if msg.lat else 0,
                        "longitude": msg.lon / 1e7 if msg.lon else 0,
                        "altitude": msg.relative_alt / 1000,  # Convert mm to meters
                        "speed": 0,  # Placeholder
                        "battery": 100,  # Placeholder
                        "heading": msg.hdg / 100 if msg.hdg else 0,
                        "satellites": 0,  # Placeholder
                        "signalStrength": 0  # Placeholder
                    }

            print(f"Sending Data: {telemetry_data}")
            send_telemetry(telemetry_data)  # Send to WebSocket
            time.sleep(1)  # Prevent spamming
