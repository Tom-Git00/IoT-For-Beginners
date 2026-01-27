import json
import network

ssid = 'IdC'
password = '12345678'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ipconfig('addr4'))

from umqtt.simple import MQTTClient

import time
import dht
from machine import Pin
led_green = Pin(6, Pin.OUT)
sensor = dht.DHT11(4)


id = '20230297'
client_name = id + 'coisa20230297'
client_telemetry_topic = id + '/telemetriaexame'
server_command_topic = id + '/comandosexame'

mqtt_client = MQTTClient(client_name, 'test.mosquitto.org')
mqtt_client.connect()
print('MQTT connected!')

def handle_command(topic, message):
    try:
        payload = json.loads(message.decode())
        print("Message received:", payload)

        if payload.get('estado_led_on') == True:
            led_green.on()
        else:
            led_green.off()
    except Exception as e:
        print(f"Error processing message: {e}")
        
    


mqtt_client.set_callback(handle_command)
mqtt_client.subscribe(server_command_topic)



while True:
  mqtt_client.check_msg()
  sensor.measure()
  valortemperatura = sensor.temperature()
  telemetry = json.dumps({'temp' : valortemperatura})

  print('Sending telemetry:', telemetry)
  

  mqtt_client.publish(client_telemetry_topic, telemetry)
    
  time.sleep(5);