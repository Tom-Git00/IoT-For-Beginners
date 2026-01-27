import json
import network
import time
from umqtt.simple import MQTTClient
from machine import Pin
import dht

# Set up Wi-Fi connection
ssid = 'IdC'
password = '12345678'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())

# Set up MQTT client
id = '20230297'
client_telemetry_topic = id + '/telemetriaexame'
client_name = id + 'servidor20230297'
server_command_topic = id + '/comandosexame'
mqtt_client = MQTTClient(client_name, 'test.mosquitto.org')
mqtt_client.connect()
print('MQTT connected!')

# Set up LEDs
led_verde = Pin(6, Pin.OUT)  # Green LED
led_amarelo = Pin(5, Pin.OUT)  # Yellow LED

# Handle command for LEDs
def handle_command(topic, message):
    payload = json.loads(message.decode())
    print("Comando recebido:", payload)

    if payload['greenwichRight']:
        led_verde.on()
        led_amarelo.off()
    else:
        led_verde.off()
        led_amarelo.on()

mqtt_client.set_callback(handle_command)
mqtt_client.subscribe(server_command_topic)

# Open GPS data file
gpsDataFile = open('gpsDataFile.txt', 'r')

def print_gps_data(data):
    data = data.strip()
    print(f"Raw data: {data}")  # Debug print to check the format
    if 'trkpt lat=' in data:
        parts = data.split('"')
        lat = float(parts[1])
        lon = float(parts[3])

        telemetry = json.dumps({'longitude': lat})
        print("A enviar:", telemetry)
        mqtt_client.publish(client_telemetry_topic, telemetry)
        mqtt_client.check_msg()

# Main loop
while True:
    data = gpsDataFile.readline()
    if not data:  # If no more data is available in the file, break the loop
        break
    print("Li a linha")
    print_gps_data(data)
    mqtt_client.check_msg()  # Process any incoming messages
    time.sleep(5)
