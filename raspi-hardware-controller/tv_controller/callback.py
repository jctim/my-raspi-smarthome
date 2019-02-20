import json
from typing import Any

import paho.mqtt.client as mqtt  # type: ignore

from . import ALEXA_CONTROL_TOPIC, ALEXA_REPLY_TOPIC, logger
from . import command_handler


def on_mqtt_connect(client: mqtt.Client, userdata: Any, flags: dict, rc: int):
    logger.debug("Connected with result code=%d, flags=%s", rc, flags)

    client.subscribe(ALEXA_CONTROL_TOPIC)
    # client.subscribe(ALEXA_REPLY_TOPIC)


def on_mqtt_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
    logger.debug("message received: topic=%s, qos=%d, retain flag=%d, payload=%s",
                 message.topic, message.qos, message.retain, message.payload)

    if message.topic == ALEXA_CONTROL_TOPIC:
        try:
            json_command = json.loads(message.payload.decode("utf-8"))
            command_handler.handle_control_command(json_command, client)
        except ValueError as err:
            logger.error("Cannot load json: %s", err)

    if message.topic == ALEXA_REPLY_TOPIC:
        pass
