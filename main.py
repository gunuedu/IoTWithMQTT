from sensor import TempHumiSensorClient
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("rasp/rcv/#")

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

def main():
    print("Rasp node-RED start..")
    mqtt_client = mqtt.Client()
    mqtt_client.connect("192.168.0.3", 1883)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect

    temphumi_client = TempHumiSensorClient("temphumi", mqtt_client)

    try:
        # Set the callback functions
        temphumi_client.run()
        mqtt_client.loop_start()
    except KeyboardInterrupt:
        pass
    finally:
        temphumi_client.mqtt_client.disconnect()

if __name__ == "__main__":
    main()