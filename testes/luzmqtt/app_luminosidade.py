import json
import paho.mqtt.client as mqtt

id = '20230297'

client_telemetry_topic = id + '/telemetriaexame'
server_command_topic = id + '/comandosexame'

def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())
    luz = payload['luz']

    print("Luminosidade:", luz)

    if luz < 2000:   # escuro
        client.publish(server_command_topic, "luzBaixa")
        print("Sent: luzBaixa")
    else:           # claro
        client.publish(server_command_topic, "luzAlta")
        print("Sent: luzAlta")

client = mqtt.Client()
client.connect("test.mosquitto.org")
client.subscribe(client_telemetry_topic)
client.on_message = handle_telemetry

print("Servidor MQTT ligado")
client.loop_forever()
