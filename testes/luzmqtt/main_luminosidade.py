import json
import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

ssid = 'IdC'
password = '12345678'

# WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    pass
print("WiFi OK")

# LEDs (como no exame)
led_green = Pin(5, Pin.OUT)
led_yellow = Pin(6, Pin.OUT)

# Sensor de luz (dado pelo professor)
light_sensor = ADC(5, atten=ADC.ATTN_0DB)

id = '20230297'
client_name = id + 'coisa20230297'
client_telemetry_topic = id + '/telemetriaexame'
server_command_topic = id + '/comandosexame'

mqtt_client = MQTTClient(client_name, 'test.mosquitto.org')
mqtt_client.connect()
mqtt_client.subscribe(server_command_topic)
print("MQTT connected!")

def handle_command(topic, message):
    comando = message.decode()
    print("Command received:", comando)

    if comando == "luzAlta":
        led_green.on()
        led_yellow.off()
    elif comando == "luzBaixa":
        led_green.off()
        led_yellow.on()

mqtt_client.set_callback(handle_command)

while True:
    mqtt_client.check_msg()

    light = light_sensor.read()
    telemetry = json.dumps({'luz': light})

    print("Sending telemetry:", telemetry)
    mqtt_client.publish(client_telemetry_topic, telemetry)

    time.sleep(15)
