# client_program.py
# This program acts as a client (like the laptop in your diagram)
# that subscribes to the final position topic and prints the results.

import paho.mqtt.client as mqtt
import json

# --- MQTT Broker Configuration ---
# This must be the same broker address as the other programs
broker_address = "192.168.106.249"
broker_port = 1883

# --- Subscription Topic ---
# This client only needs to subscribe to the final position topic
position_topic = "home/position"

# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the client connects to the MQTT broker.
    """
    if rc == 0:
        print("Client connected to MQTT Broker!")
        # Subscribe to the position topic
        client.subscribe(position_topic)
        print(f"Subscribed to topic: {position_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """
    Callback function for when a message is received on the subscribed topic.
    """
    try:
        # Decode the message payload and parse it as JSON
        message_json = msg.payload.decode()
        data = json.loads(message_json)
        
        # Extract and print the key information from the JSON message
        tracked_device = data.get("uuid", "N/A")
        session = data.get("session_id", "N/A")
        position = data.get("calculated_position", {"x": "N/A", "y": "N/A", "z": "N/A"})
        
        print("-" * 40)
        print(f"New Position Update!")
        print(f"Tracked Device UUID: {tracked_device}")
        print(f"Session ID: {session}")
        print(f"Calculated Position: X={position['x']}, Y={position['y']}, Z={position['z']}")
        print("-" * 40)
            
    except json.JSONDecodeError:
        print("Error decoding JSON from message.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Main Program ---
def main():
    """
    Initializes the MQTT client and starts the message loop.
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(broker_address, broker_port, 60)
        
        # Start a loop to listen for incoming messages indefinitely
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
