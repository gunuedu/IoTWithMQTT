import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import tm1637
import threading
import time

# TM1637을 설정할때 Borad connector pin번호를 입력하는것이 아니고 BCM의 실제 GPIO 번호를 입력해야함.
# CLK -> GPIO23 (Pin 16)
# Di0 -> GPIO24 (Pin 18)
tm = tm1637.TM1637(22, 23)

class Sensor:
    def __init__(self, sensor_type, mqtt_client):
        GPIO.setmode(GPIO.BOARD)
        # LED On/Off
        GPIO.setup(12, GPIO.OUT)
        # Motor Test
        GPIO.setup(36, GPIO.OUT)
        # 초기값 = On
        GPIO.output(12, GPIO.HIGH)

        self.next_t = time.time()
        self.increment = 2
        self.sensor_type = sensor_type
        self.mqtt_client = mqtt_client
        self.mqtt_client.on_message = self.on_message # set the callback for incomming message.
        self.setup_sensor()
        print(f"Sensor : {sensor_type} {mqtt_client} constructed..")

    def publish_data(self, topic, payload):
        self.mqtt_client.publish(topic, payload)

    def on_message(self, client, userdata, message):
        received_message = message.payload.decode("utf-8")
        print(f"Rasp Node rcv message on topic {message.topic}: {received_message}")
        if message.topic == "rasp/rcv/led":
            if received_message == "off":
                GPIO.output(12, GPIO.LOW)
                print(f"received off.")

            elif received_message == "on":
                GPIO.output(12, GPIO.HIGH)
                print(f"received on.")

        if message.topic == "rasp/rcv/humimotor":
            if received_message == "off":
                GPIO.output(12, GPIO.LOW)
                print(f"received off.")

            elif received_message == "on":
                GPIO.output(12, GPIO.HIGH)
                print(f"received on.")

        if message.topic == "rasp/rcv/motor":
            if received_message == "off":
                GPIO.output(36, GPIO.LOW)
                print(f"received off.")

            elif received_message == "on":
                GPIO.output(36, GPIO.HIGH)
                print(f"received on.")

            elif received_message == "do_something":
                self.do_someting()

    def do_someting(self):
        # Handle command from broket.
        pass

#-------------------- Temp&Humi Sensor ---------------------#

class TempHumiSensorClient(Sensor):

    def setup_sensor(self):
        print(f"Temp & Humi sensor_setup.")

    def report_light_level(self):
        segment = "    "
        tm.show(segment, colon=True)
        humidity, temperature = dht.read_retry(dht.DHT22, 4)
        humi = round(humidity, 3)
        temp = round(temperature, 3)
        print(f"{time.ctime()} : Temp: {temp}    Humi: {humi}")
        self.publish_data(f"rasp/send/temp", temp)
        self.publish_data(f"rasp/send/humi", humi)
        segment = str(round(temp))+str(round(humi))
        tm.show(segment, colon=True)
        # tm.write([127, 255, 127, 127])

    def run(self):
        print(f"Temp & Humi SensorClient run..")
        def report_periodically():
            self.report_light_level()
            self.next_t += self.increment
            # self.timer = threading.Timer(2, report_periodically)  # Report every 2 seconds
            self.timer = threading.Timer(self.next_t - time.time(), report_periodically)
            self.timer.start()

        # self.timer = threading.Timer(2, report_periodically)  # Initial start
        self.timer = threading.Timer(self.next_t - time.time(), report_periodically)
        self.timer.start()