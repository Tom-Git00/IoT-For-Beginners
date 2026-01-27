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

def turn_off_later(client):    
    # Enviar comando para desligar
    command = {'estado_led_on': False}
    client.publish(server_command_topic, json.dumps(command))
    


def handle_telemetry(client, message):
    global ignoring_messages
    if ignoring_messages:
        print("Ignorando mensagem recebida durante o período de espera.")
        return
   
    estado = json.loads(message.payload.decode())
    print("Message received:", estado)
    temperatura = estado.get('temp')
    
    if temperatura < 80:
        print("Temperatura abaixo de 80°C. Ligando LED verde.")
        command = {'estado_led_on': True}
        client.publish(server_command_topic, json.dumps(command))
        
        ignoring_messages = True
        turn_off_later(client)
        time.sleep(20)  
    else:
        print("Temperatura acima de 80°C. Desligando LED.") 
        client.publish(server_command_topic, json.dumps({'estado_led_on': False}))
    
    time.sleep(20)


mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.loop_forever()
