# master_rpi_program.py
# This program acts as the master node. It subscribes to all raw data topics,
# performs a calculation, and publishes the final position.

import paho.mqtt.client as mqtt
import time
import json

# --- MQTT Broker Configuration ---
broker_address = "192.168.106.249"
broker_port = 1883

# --- Master Node Topics ---
# The master node subscribes to all raw data topics using a wildcard "+"
raw_data_topic = "uwb/raw_data/+"
# The master node publishes to this single position topic
position_topic = "uwb/position"

# --- Placeholder for Calculations ---
# In a real-world system, this is where your localization algorithm would go.
def perform_calculation(all_raw_data):
    """
    This function simulates the "Calculations" block from your diagram.
    
    It receives a dictionary containing raw data from all nodes (keys are UUIDs).
    You would replace the placeholder code here with your multilateration or
    triangulation algorithm to compute the final position.
    
    Returns a dictionary with the calculated position.
    """
    print("\nStarting calculation...")
    
    # Placeholder: In the real code, you would use data from multiple nodes
    # to calculate a single, precise position.
    # For now, we'll just average the incoming XYZ values.
    
    avg_x = sum(d['xyz']['x'] for d in all_raw_data.values()) / len(all_raw_data)
    avg_y = sum(d['xyz']['y'] for d in all_raw_data.values()) / len(all_raw_data)
    avg_z = sum(d['xyz']['z'] for d in all_raw_data.values()) / len(all_raw_data)
    
    # Assuming a single iPhone is being tracked, we can use a static UUID for the output
    # or the UUID of the iPhone itself.
    output_data = {
        "uuid": "iphone_tracked_device", 
        "session_id": list(all_raw_data.values())[0]['session_id'],
        "calculated_position": {
            "x": round(avg_x, 2),
            "y": round(avg_y, 2),
            "z": round(avg_z, 2)
        }
    }
    
    print("Calculation complete.")
    return output_data

# Store incoming data from all nodes until ready to calculate
incoming_data = {}

# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the master client connects to the MQTT broker.
    """
    if rc == 0:
        print("Master RPI connected to MQTT Broker!")
        # Subscribe to all raw data topics from all nodes
        client.subscribe(raw_data_topic)
        print(f"Subscribed to topic: {raw_data_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """
    Callback function for when a message is received on a subscribed topic.
    """
    try:
        # Decode the message from bytes to a JSON string, then parse it
        message_json = msg.payload.decode()
        data = json.loads(message_json)
        
        node_uuid = data['uuid']
        
        # Store the incoming data from this node
        incoming_data[node_uuid] = data
        print(f"Received data from '{msg.topic}': {data}")
        
        # We need data from at least 3 nodes for triangulation in 3D space.
        # This condition triggers the calculation.
        if len(incoming_data) >= 3:
            print(f"\nCollected data from {len(incoming_data)} nodes. Ready to calculate.")
            
            # Perform the calculation with the collected data
            calculated_position = perform_calculation(incoming_data)
            
            # Publish the final calculated position to the position topic
            client.publish(position_topic, json.dumps(calculated_position))
            print(f"Published final position to '{position_topic}': {calculated_position}\n")
            
            # Clear the collected data to prepare for the next round of calculations
            incoming_data.clear()
            
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
# --- Main Program ---
def main():
    """
    Initializes the MQTT client, sets up callbacks, and starts the loop.
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(broker_address, broker_port, 60)
        
        # Start the network loop, blocking until disconnect.
        # This client will wait for messages indefinitely.
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
