#!/usr/bin/python

from ppadb.client import Client as AdbClient
import paho.mqtt.client as mqtt
from os import environ as env
import logging
import json

def main():
    logging.basicConfig(level=logging.INFO)

    broker_host = env.get('BROKER_HOST') or "localhost"
    broker_port = env.get('BROKER_PORT') or 1883
    server_host = env.get('ADB_SERVER_HOST') or "localhost"
    server_port = env.get('ADB_SERVER_PORT') or 5037
    device_host = env.get('ADB_DEVICE_HOST') or "localhost"
    device_port = env.get('ADB_DEVICE_PORT') or 5555
    ha_topic = env.get('HA_TOPIC') or 'homeassistant'
    topic = env.get('MQTT_TOPIC') or "dash_control"
    device_name = env.get('DEVICE_NAME') or "Dashboard Screen"

    logging.info("Using adb server: %s:%s", server_host, server_port)

    availability_topic = topic + "/status"
    state_topic = topic + "/switch/screen/state"
    config_topic = ha_topic + "/switch/" + topic + "/screen/config"
    command_topic = topic + "/switch/screen/set"

    client = AdbClient(host=server_host, port=server_port)

    client.remote_connect(device_host, device_port)

    device = client.device(device_host + ":" + str(device_port))

    def on_connect(client, userdata, flags, rc):
        logging.info("Connected to adb device: %s:%s", device_host, device_port)

        client.message_callback_add(command_topic, on_command)

        client.publish(availability_topic, payload="online", retain=True)
        client.publish(state_topic, payload="OFF", retain=True)
        ha_discover(client)

    def on_message(client, userdata, msg):
        logging.info("%s %s", msg.topic, msg.payload)

    def on_command(client, userdata, msg):
        if msg.payload == b'on':
            logging.info("Wake up screen")
            device.shell("input keyevent KEYCODE_WAKEUP")
            client.publish(state_topic, payload="ON", retain=True)
        else:
            logging.info("Power off screen")
            device.shell("input keyevent KEYCODE_POWER")
            client.publish(state_topic, payload="OFF", retain=True)

    def ha_discover(client):
        config = {
            "name": device_name,
            "state_topic": state_topic,
            "command_topic": command_topic,
            "availability_topic": availability_topic,
            "unique_id": state_topic + "_screen",
            "device": {
                "identifiers": "840d8e64fbe1",
                "name": device_name,
                "sw_version": "1",
                "model": "mqtt2adb",
                "manufacturer": "kubiq"
            }
        }
        client.publish(config_topic, payload=json.dumps(config), retain=True)


    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.will_set(availability_topic, payload="offline")
    client.connect(broker_host, broker_port, 60)

    client.loop_forever()


if __name__ == '__main__':
    main()
