import json
import time
import paho.mqtt.client as mqtt

id = '20230297'

client_telemetry_topic = id + '/telemetriaexame'
client_name = id + 'servidor20230297'
server_command_topic = id + '/comandosexame'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')

ignoring_messages = False
mqtt_client.loop_start()

print("MQTT connected!")

def handle_telemetry(client, userdata, message):
    global ignoring_messages

    if ignoring_messages:
        print("Ignorando mensagem durante período de espera")
        return

    estado = json.loads(message.payload.decode())
    print("Message received:", estado)

    temperatura = estado.get('temp')

    if temperatura >= 22:
        print("Temperatura superior a 22°C → tempSup")
        client.publish(server_command_topic, "tempSup")
    else:
        print("Temperatura inferior a 22°C → tempInf")
        client.publish(server_command_topic, "tempInf")

    ignoring_messages = True
    time.sleep(15)
    ignoring_messages = False

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

mqtt_client.loop_forever()
