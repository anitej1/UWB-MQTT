# new_master_rpi_program.py
# This program is the master node. It subscribes to all node topics,
# parses the string message, performs a calculation, and publishes the result.

import paho.mqtt.client as mqtt
import time
import json

# --- MQTT Broker Configuration ---
broker_address = "192.168.106.249"
broker_port = 1883

# --- Master Node Topics ---
# The master node subscribes to all node topics using a wildcard "+"
raw_data_topic = "home/nodes/+"
# The master node publishes to this single position topic
position_topic = "home/position"

# --- Placeholder for Calculations ---
def perform_calculation(all_raw_data):
    """
    This function simulates the "Calculations" block from your diagram.
    
    It receives a dictionary containing raw data from all nodes.
    It performs a simple average as a placeholder for a localization algorithm.
    
    Returns a dictionary with the calculated position.
    """
    print("\nStarting calculation...")
    
    # Calculate the average position from all received data points
    avg_x = sum(d['xyz']['x'] for d in all_raw_data.values()) / len(all_raw_data)
    avg_y = sum(d['xyz']['y'] for d in all_raw_data.values()) / len(all_raw_data)
    avg_z = sum(d['xyz']['z'] for d in all_raw_data.values()) / len(all_raw_data)
    
    # Create the output data dictionary, which will be converted to JSON
    output_data = {
        "uuid": list(all_raw_data.values())[0]['uuid'], 
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
    Callback function for when a message is received.
    It parses the string message and stores the data.
    """
    try:
        # The topic gives us the node name
        node_name = msg.topic.split("/")[-1]
        
        # Decode the message from bytes to a string
        message_string = msg.payload.decode()
        
        # Parse the string message to extract the data
        parts = message_string.split('/')
        if len(parts) == 3:
            node_uuid, session_id, xyz_string = parts
            x, y, z = map(float, xyz_string.split(','))
            
            data = {
                "uuid": node_uuid,
                "session_id": session_id,
                "xyz": {"x": x, "y": y, "z": z}
            }
            
            # Store the incoming data from this node
            incoming_data[node_name] = data
            print(f"Received data from '{node_name}': {data}")
            
            # We need data from at least 3 nodes for triangulation in 3D space.
            if len(incoming_data) >= 3:
                print(f"\nCollected data from {len(incoming_data)} nodes. Ready to calculate.")
                
                # Perform the calculation with the collected data
                calculated_position = perform_calculation(incoming_data)
                
                # Publish the final calculated position to the position topic
                client.publish(position_topic, json.dumps(calculated_position))
                print(f"Published final position to '{position_topic}': {calculated_position}\n")
                
                # Clear the collected data
                incoming_data.clear()
        
    except (ValueError, IndexError) as e:
        print(f"Error parsing message from '{msg.topic}': {e}")
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
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
