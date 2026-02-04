import json
import network
import time
from machine import Pin
import dht
from umqtt.simple import MQTTClient

# --- CONFIGURAÇÃO DE REDE ---
ssid = '<NETWORK_SSID>'
password = '<NETWORK_PASSWORD>'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print('Network config:', wlan.ipconfig('addr4'))

# --- CONFIGURAÇÃO DE HARDWARE (Conforme enunciado) ---
# Sensor de Temperatura DHT11 no GPIO36
sensor = dht.DHT11(Pin(36)) 

# LED Verde no GPIO8
led_verde = Pin(8, Pin.OUT)

# LED Amarelo no GPIO3
led_amarelo = Pin(3, Pin.OUT)

# Relé no GPIO14
rele = Pin(14, Pin.OUT)

# --- CONFIGURAÇÃO MQTT (Conforme regras) ---
aluno_id = '20231017' # Número retirado da folha
broker = 'test.mosquitto.org'

client_name = aluno_id + 'dispositivo2026'
topic_telemetry = aluno_id + '/tel2026'
topic_command = aluno_id + '/com2026'

print(f"ID Cliente: {client_name}")
mqtt_client = MQTTClient(client_name, broker)

# --- FUNÇÃO CALLBACK (Receber comandos do servidor) ---
def handle_command(topic, message):
    try:
        payload = json.loads(message.decode())
        print("Mensagem recebida do servidor:", payload)
        
        if 'activa' in payload:
            estado = payload['activa']
            
            # Lógica dos Estados (0, 1, 2)
            if estado == 0:
                print("Estado 0: Tudo Desligado")
                led_verde.off()
                led_amarelo.off()
                rele.off()
                
            elif estado == 1:
                print("Estado 1: Amarelo ON")
                led_verde.off()
                led_amarelo.on()
                rele.off()
                
            elif estado == 2:
                print("Estado 2: Verde e Relé ON")
                led_verde.on()
                led_amarelo.off()
                rele.on()
                
    except Exception as e:
        print("Erro ao processar mensagem:", e)

# --- LOOP PRINCIPAL ---
try:
    mqtt_client.set_callback(handle_command)
    mqtt_client.connect()
    mqtt_client.subscribe(topic_command)
    print("MQTT conectado e subscrito!")

    while True:
        try:
            # Ler temperatura
            sensor.measure()
            temp = sensor.temperature()
            
            # Criar JSON conforme regra: {'temperatura': valorTemperatura}
            telemetry = json.dumps({'temperatura': temp})
            
            print(f"Enviando temperatura: {temp}°C")
            mqtt_client.publish(topic_telemetry, telemetry)
            
            # Verificar mensagens recebidas (non-blocking se possível, mas aqui usamos check_msg)
            mqtt_client.check_msg()
            
        except OSError as e:
            print("Erro ao ler sensor ou publicar:", e)

        # Esperar 15 segundos conforme enunciado
        time.sleep(15)

except Exception as e:
    print("Erro fatal:", e)
    # mqtt_client.disconnect()