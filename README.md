mqtt2adb
========

Wake up your Android device with MQTT!

What does it do? It subscribes to mqtt topic and listens for messages, which it translates to adb commands.

## Requirements:
* Android device with debugging on
* Adb server `https://github.com/sorccu/docker-adb` is tested and working

### env variables:
* `BROKER_HOST` mqtt address `localhost`
* `BROKER_PORT` mqtt port `1883`
* `ADB_SERVER_HOST` Adb server address `localhost`
* `ADB_SERVER_PORT` Adb server port `5037`
* `ADB_DEVICE_HOST` ip address of device `localhost`
* `ADB_DEVICE_PORT` port of device `5555`
* `MQTT_TOPIC topic` on which listen for commands `dash_control`
* `HA_TOPIC topic` topic for Home Assistant autodiscovery `homeassistant`

### Use docker to run:
`docker run -e BROKER_HOST=192.168.1.5 -e ADB_SERVER_HOST=192.168.1.5 -e ADB_DEVICE_HOST=192.168.1.75 thebiftek/mqtt2adb`

### Wake up command:
Topic: `dash_control/screen/state`

Payload: `on`

### Power off screen command:
Topic: `dash_control/screen/state`

Payload: `off`

### Integration with Home Assistant:
Device will be discovered by Home Assistant automatically when used with mqtt

