# new_rpi_node_program.py
# This program simulates an individual RPI node. It publishes data as a string
# to a topic in the format "home/nodes/".

import paho.mqtt.client as mqtt
import time
import uuid

# --- MQTT Broker Configuration ---
# Replace with the IP address or hostname of your MQTT broker
broker_address = "192.168.106.249"
broker_port = 1883

# --- Node-Specific Configuration ---
# A friendly name for this node, used in the topic.
node_name = "node_a"
# A unique identifier for the UWB board, which might be hardcoded or read.
node_uuid = str(uuid.uuid4())
session_id = str(uuid.uuid4())[:8] # A shorter ID for demonstration

print(f"Node Name: {node_name}")
print(f"Node UUID: {node_uuid}")

# --- Data Simulation (replace with your UWB board logic) ---
def get_uwb_data():
    """
    This function simulates reading data from a UWB board.
    
    It generates simulated ranging data. In your actual application, you would
    replace this with the code that reads data from the UWB board (e.g., via UART).
    
    Returns a string in the format "UUID/session_ID/X,Y,Z".
    """
    global session_id # Use a global session ID for this example
    
    # Increment the session ID to show new data rounds
    session_id = str(int(session_id, 16) + 1)[-8:]
    
    x = 1.0 + time.time() % 10
    y = 5.0 - time.time() % 8
    z = 3.0 + time.time() % 5
    
    # Format the data into the requested string format
    data_string = f"{node_uuid}/{session_id}/{x:.2f},{y:.2f},{z:.2f}"
    
    return data_string

# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the client connects to the MQTT broker.
    """
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Publish an "online" status message when connecting
        client.publish(f"home/status/{node_name}", "online", retain=True)
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    """
    Callback function for when the client disconnects.
    """
    print("Disconnected from MQTT Broker.")
    # Publish an "offline" status message on unexpected disconnect
    if rc != 0:
        client.publish(f"home/status/{node_name}", "offline", retain=True)

# --- Main Program ---
def main():
    """
    Initializes the MQTT client and starts the data publishing loop.
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    # Set up Last Will and Testament (LWT) message
    client.will_set(f"home/status/{node_name}", "offline", retain=True)
    
    try:
        # Connect to the broker
        client.connect(broker_address, broker_port, 60)
        client.loop_start() # Start a background thread
        
        # Define the topic to publish to
        publish_topic = f"home/nodes/{node_name}"
        
        while True:
            # Get the simulated UWB data string
            uwb_data_string = get_uwb_data()
            
            # Publish the string message to the node's specific topic
            client.publish(publish_topic, uwb_data_string)
            print(f"Published to '{publish_topic}': {uwb_data_string}")
            
            # Wait before the next publish
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        
if __name__ == "__main__":
    main()
