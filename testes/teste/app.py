import json
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÃO (Conforme regras) ---
aluno_id = '20231017' # Número retirado da folha
broker = 'test.mosquitto.org'

client_name = aluno_id + 'servidor2026'
topic_telemetry = aluno_id + '/tel2026'   # Tópico onde o servidor ESCUTA
topic_command = aluno_id + '/com2026'     # Tópico onde o servidor FALA

# --- LÓGICA DO SERVIDOR ---
def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print("Recebido do dispositivo:", payload)

        if 'temperatura' in payload:
            temp = payload['temperatura']
            estado_a_enviar = 0

            # Lógica de decisão baseada na temperatura
            if temp < 20:
                estado_a_enviar = 0
            elif 20 <= temp <= 22:
                estado_a_enviar = 1
            elif temp > 22:
                estado_a_enviar = 2

            # Formato da mensagem JSON de comando: {'activa': estado}
            comando = {'activa': estado_a_enviar}
            
            print(f"Temperatura: {temp}°C -> Enviando Estado: {estado_a_enviar}")
            client.publish(topic_command, json.dumps(comando))
            
    except Exception as e:
        print("Erro ao processar dados:", e)

# --- INICIALIZAÇÃO MQTT ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_name) # Atualizado para nova versão do Paho
# Se der erro na linha acima por versão antiga, usa: mqtt_client = mqtt.Client(client_name)

mqtt_client.on_message = handle_telemetry

print(f"Conectando ao broker {broker}...")
mqtt_client.connect(broker)
mqtt_client.subscribe(topic_telemetry)
print(f"Servidor {client_name} online. Aguardando mensagens em {topic_telemetry}...")

# Mantém o script a correr
mqtt_client.loop_forever()