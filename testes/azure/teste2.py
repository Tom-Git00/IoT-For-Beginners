
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

try:
    import ioth
except:
    import mip
    mip.install('github:jcaldeira-iot/iot-hub-micropython-client/package.json')
    import ioth
from ioth import IoTHClient, IoTHEvents

iot_hub = 'hname20230297.azure-devices.net'
device_id = 'did20230297'
sas_token = 'SharedAccessSignature sr=hname20230297.azure-devices.net%2Fdevices%2Fdid20230297&sig=ddyc%2Bg77G5YHR3%2B9hqqQzHblnvrTAFADO09vTibgQ6w%3D&se=1770178547'

device_client = IoTHClient(iot_hub, device_id, sas_token)

print('Connecting')
device_client.connect()
print('Connected')

import time
from machine import ADC, Pin
import dht


ledverde = Pin(6, Pin.OUT)
ledyellow = Pin(5, Pin.OUT)
sensor = dht.DHT11(7)
temp = sensor.temperature()

def handle_method_request(request, ack):
    print("Direct method received - ", request.name)

    if request.name == "tempSup":
        ledverde.on()
        ledyellow.off()
    elif request.name == "tempInf":
        ledverde.off()
        ledyellow.on()
        
    ack(request, "200")
    
device_client.on(IoTHEvents.COMMANDS, handle_method_request)

sec_count = 0

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        print(f"Temperature {temp}°C")
    except:
        print("Erro ao ler DHT11")
        time.sleep(2)
        continue

    if temp > 25:
        ledverde.off()
        ledyellow.on()
    else:
        ledverde.on()
        ledyellow.off()

    if sec_count == 0:
        telemetry = json.dumps({'temp': temp})
        print("Sending telemetry", telemetry)
        device_client.send_telemetry(telemetry)

    device_client.listen()
    sec_count = (sec_count + 1) % 10
    time.sleep(1)
