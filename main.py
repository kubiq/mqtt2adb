#!/usr/bin/python

from ppadb.client import Client as AdbClient
import paho.mqtt.client as mqtt
from os import environ as env
import logging


def main():
    logging.basicConfig(level=logging.INFO)

    broker_host = env.get('BROKER_HOST') or "localhost"
    broker_port = env.get('BROKER_PORT') or 1883
    server_host = env.get('ADB_SERVER_HOST') or "localhost"
    server_port = env.get('ADB_SERVER_PORT') or 5037
    device_host = env.get('ADB_DEVICE_HOST') or "localhost"
    device_port = env.get('ADB_DEVICE_PORT') or 5555
    topic = env.get('MQTT_TOPIC') or "dash_control"

    logging.info("Using adb server: %s:%s", server_host, server_port)

    client = AdbClient(host=server_host, port=server_port)

    client.remote_connect(device_host, device_port)

    device = client.device(device_host + ":" + str(device_port))

    def on_connect(client, userdata, flags, rc):
        logging.info("Connected to adb device: %s:%s", device_host, device_port)

        client.subscribe(topic + "/#")

        client.message_callback_add(topic + "/screen/state", on_screen_message)

        client.publish(topic + "/status", payload="online")

    def on_message(client, userdata, msg):
        logging.info("%s %s", msg.topic, msg.payload)

    def on_screen_message(client, userdata, msg):
        if msg.payload == b'on':
            logging.info("Wake up")
            device.shell("input keyevent KEYCODE_WAKEUP")
            client.publish(topic + "/screen/state")
        else:
            logging.info("Power off screen")
            device.shell("input keyevent KEYCODE_POWER")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.will_set(topic + "/status", payload="offline")
    client.connect(broker_host, broker_port, 60)

    client.loop_forever()

if __name__ == '__main__':
    main()
