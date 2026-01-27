import json
import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

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

# Hardware conforme enunciado
led_green = Pin(5, Pin.OUT)
led_yellow = Pin(6, Pin.OUT)
sensor = dht.DHT11(Pin(7))

id = '20230297'
client_name = id + 'coisa20230297'
client_telemetry_topic = id + '/telemetriaexame'
server_command_topic = id + '/comandosexame'

mqtt_client = MQTTClient(client_name, 'test.mosquitto.org')
mqtt_client.connect()
print('MQTT connected!')

def handle_command(topic, message):
    try:
        comando = message.decode()
        print("Command received:", comando)

        if comando == "tempSup":
            led_yellow.on()
            led_green.off()
        elif comando == "tempInf":
            led_yellow.off()
            led_green.on()
    except Exception as e:
        print("Error:", e)

mqtt_client.set_callback(handle_command)
mqtt_client.subscribe(server_command_topic)

while True:
    mqtt_client.check_msg()

    sensor.measure()
    valortemperatura = sensor.temperature()

    telemetry = json.dumps({'temp': valortemperatura})
    print('Sending telemetry:', telemetry)

    mqtt_client.publish(client_telemetry_topic, telemetry)

    time.sleep(15)
