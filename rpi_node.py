# rpi_node_program.py
# This program simulates an individual RPI node reading data from a UWB board
# and publishing it to a unique MQTT topic.

import paho.mqtt.client as mqtt
import time
import json
import uuid

# --- MQTT Broker Configuration ---
# Replace with the IP address or hostname of your MQTT broker
broker_address = "192.168.106.249"
broker_port = 1883

# --- Node-Specific Configuration ---
# Generate a unique ID for this RPI node. In a real-world scenario, you might
# hardcode this or read it from a configuration file.
node_uuid = str(uuid.uuid4())
print(f"Node UUID: {node_uuid}")

# Define the topic for this specific node
raw_data_topic = f"uwb/raw_data/{node_uuid}"

# --- Data Simulation (replace with your UWB board logic) ---
def get_uwb_data():
    """
    This function simulates reading data from a UWB board.
    
    In your actual application, you would replace this with the code that reads
    ranging data from the UWB board, which is likely connected via UART.
    The data structure should include session_id, and XYZ coordinates.
    
    Returns a dictionary with simulated ranging data.
    """
    session_id = str(uuid.uuid4())[:8] # A shorter ID for demonstration
    x = 1.0 + time.time() % 10 # Simulates a changing value
    y = 5.0 - time.time() % 8
    z = 3.0 + time.time() % 5
    
    data = {
        "uuid": node_uuid,
        "session_id": session_id,
        "xyz": {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
    }
    return data

# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the client connects to the MQTT broker.
    """
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Publish an "online" status message when connecting
        client.publish(f"uwb/status/{node_uuid}", "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    """
    Callback function for when the client disconnects from the MQTT broker.
    """
    print("Disconnected from MQTT Broker.")
    # Publish an "offline" status message on unexpected disconnect
    if rc != 0:
        client.publish(f"uwb/status/{node_uuid}", "offline", retain=True)

# --- Main Program ---
def main():
    """
    Initializes the MQTT client and starts the data publishing loop.
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    # Set up Last Will and Testament (LWT) message
    client.will_set(f"uwb/status/{node_uuid}", "offline", retain=True)
    
    try:
        # Connect to the broker
        client.connect(broker_address, broker_port, 60)
        client.loop_start() # Start a background thread for network communication
        
        while True:
            # Get the simulated UWB data
            uwb_data = get_uwb_data()
            
            # Convert the data dictionary to a JSON string
            message = json.dumps(uwb_data)
            
            # Publish the message to the node's specific topic
            client.publish(raw_data_topic, message)
            print(f"Published to '{raw_data_topic}': {message}")
            
            # Wait for a few seconds before the next publish
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop the background thread and disconnect gracefully
        client.loop_stop()
        client.disconnect()
        
if __name__ == "__main__":
    main()
