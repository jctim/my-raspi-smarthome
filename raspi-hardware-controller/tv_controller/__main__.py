import os
import sys
from urllib.parse import urlparse, ParseResult

import paho.mqtt.client as mqtt  # type:ignore

from . import callback
from . import logger, DEVICE_ID


def main():
    url: str = os.environ.get('MQTT_BROKER_URL', 'mqtt://localhost:1883')
    connection: ParseResult = urlparse(url)

    client = mqtt.Client(client_id='tv-controller_{}'.format(DEVICE_ID), clean_session=True, userdata=None, transport='tcp')
    client.username_pw_set(connection.username, connection.password)
    if connection.scheme == "mqtts":
        client.tls_set()

    client.on_connect = callback.on_mqtt_connect
    client.on_message = callback.on_mqtt_message

    client.connect(connection.hostname, connection.port)

    logger.debug('main started with sys args: %s', str(sys.argv))
    client.loop_forever()


if __name__ == '__main__':
    main()
