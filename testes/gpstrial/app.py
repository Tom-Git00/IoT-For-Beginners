import json
import time
import paho.mqtt.client as mqtt

id = '20230297'

client_telemetry_topic = id + '/telemetriaexame'
client_name = id + 'servidor20230297'
server_command_topic = id + '/comandosexame'

# Create MQTT client
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')

mqtt_client.loop_start()
print("MQTT connected!")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Recebido:", payload)

        # Check if the payload contains the longitude key
        if 'longitude' in payload:
            estado = payload['longitude'] > 0  # TRUE se longitude > 0

            # Create command to send back
            command = {'greenwichRight': estado}
            print("A enviar comando:", command)

            # Publish the command to the server
            client.publish(server_command_topic, json.dumps(command))
        else:
            print("Payload does not contain 'longitude' key.")

    except Exception as e:
        print(f"Error processing message: {e}")


# Subscribe to the telemetry topic
mqtt_client.subscribe(client_telemetry_topic)

# Set callback for message reception
mqtt_client.on_message = on_message

# Main loop to keep the program running
try:
    while True:
        mqtt_client.loop()  # Process incoming messages and handle callbacks
        time.sleep(1)  # Optional: gives some CPU breathing room
except KeyboardInterrupt:
    print("Exiting...")
    mqtt_client.loop_stop()  # Stop the loop if exiting
    mqtt_client.disconnect()  # Disconnect the client
