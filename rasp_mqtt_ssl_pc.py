import paho.mqtt.client as mqtt
import time
import ssl

# MQTT 브로커 정보 설정
mqtt_broker_host = "192.168.0.2"  # MQTT 브로커의 IP 주소나 호스트명
mqtt_broker_port = 8883  # MQTT 브로커의 포트 (기본 포트는 1883입니다.)

# MQTT 클라이언트 생성
client = mqtt.Client("RaspberryPiClient")

# Callback function for successful connection
def on_connect(client, userdata, flags, rc):
    client.subscribe("rasp/rcv/#")
    print(f"Connected with result code {rc}")

# Callback function for disconnection
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection. Reconnecting...")
        while True:
            try:
                client.reconnect()
                break  # Exit the loop if reconnection is successful
            except:
                time.sleep(5)

# 메시지를 발행 (Publish)하는 함수
def publish_message(topic, message):
    client.publish(topic, message)
    print(f"rasp Published to {topic}: {message}")


def on_message(client, userdata, message):
    received_message = message.payload.decode("utf-8")
    print(f"{time.ctime()} rasp is running. ")
    print(f"rasp Received message on topic {message.topic}: {received_message}")

def on_pre_connect(client, userdata):
    print(f"rasp on_pre_connect...")

# Set the callback functions
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_pre_connect = on_pre_connect
client.tls_set("/home/gunu/certsPC/ca.crt", "/home/gunu/certsPC/client.crt", "/home/gunu/certsPC/client.key", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(False)

# MQTT 루프 시작
client.connect(mqtt_broker_host, mqtt_broker_port, 60)

try:
    print(f"rasp Node-RED client start.....")
    client.loop_start()

    while True:
        print(f"{time.ctime()} rasp is running. ")
        publish_message("rasp/send/dev", "from rasp")
        time.sleep(5)

except KeyboardInterrupt:
    print(f"Keyboard Interrupt, Stop Node-RED.....")

finally:
    client.disconnect()
