#!/usr/bin/python

from ppadb.client import Client as AdbClient
import paho.mqtt.client as mqtt
from os import environ as env

adbServer = env.get('ADB_SERVER') or "localhost"
print("Using adb server: " + adbServer)

client = AdbClient(host="192.168.1.5", port=5037)

client.remote_connect("192.168.1.75", 5555)

device = client.device("192.168.1.75:5555")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("dashboard_control/#")

    client.message_callback_add("dashboard_control/screen/state", on_screen_message)

    client.publish("dashboard_control/status", payload="online")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_screen_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    if msg.topic == "dashboard_control/screen/state":
        print(str(msg.payload))
        if str(msg.payload) == "on":
            device.shell("input keyevent KEYCODE_WAKEUP")
        else:
            device.shell("input keyevent KEYCODE_POWER")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.will_set("dashboard_control/status", payload="offline")
client.connect("192.168.1.5", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
