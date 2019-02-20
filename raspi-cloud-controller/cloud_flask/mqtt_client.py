import logging
import uuid
from typing import Any, Optional, List
from urllib.parse import urlparse, ParseResult

import paho.mqtt.client as mqtt  # type:ignore
from flask import Flask, logging as flask_logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(flask_logging.default_handler)
_LOGGER.setLevel(logging.DEBUG)

_mqtt_client: Optional[mqtt.Client] = None  # TODO a global app context for objects like this


def init_app(app: Flask):
    global _mqtt_client
    _mqtt_client = _create_mqtt_client(app)


def get() -> mqtt.Client:
    return _mqtt_client


def disconnect() -> None:
    _LOGGER.debug("disconnect: %s", _mqtt_client)
    if _mqtt_client is not None:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()


def _create_mqtt_client(app: Flask) -> mqtt.Client:
    url: str = app.config['MQTT_BROKER_URL']
    connection: ParseResult = urlparse(url)

    client = mqtt.Client(client_id='cloud-controller-{}'.format(uuid.uuid4()),
                         clean_session=True,
                         userdata=None,
                         transport='tcp')
    client.username_pw_set(connection.username, connection.password)
    if connection.scheme == "mqtts":
        client.tls_set()

    client.on_connect = _on_mqtt_connect
    client.on_message = _on_mqtt_message
    client.on_subscribe = _on_mqtt_subscribe
    client.on_unsubscribe = _on_mqtt_unsubscribe

    client.connect(connection.hostname, connection.port)

    client.loop_start()
    return client


def _on_mqtt_subscribe(client: mqtt.Client, userdata: Any, mid: int, granted_qos: List[int]):
    _LOGGER.debug("Subscribed by client %s with userdata=%s, mid=%d, qos=%s", client, userdata, mid, granted_qos)


def _on_mqtt_unsubscribe(client: mqtt.Client, userdata: Any, mid: int):
    _LOGGER.debug("Unsubscribed by client %s with userdata=%s, mid=%d", client, userdata, mid)


def _on_mqtt_connect(client: mqtt.Client, userdata: Any, flags: dict, rc: int):
    _LOGGER.debug("Connected by client %s with result code=%d, flags=%s", client, rc, flags)


def _on_mqtt_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
    _LOGGER.debug("message received by client %s: topic=%s, qos=%d, retain flag=%s, payload=%s",
                  client, message.topic, message.qos, message.retain, message.payload)
