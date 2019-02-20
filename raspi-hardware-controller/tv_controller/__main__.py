import os
import sys
import uuid
from urllib.parse import urlparse, ParseResult

import paho.mqtt.client as mqtt  # type:ignore

from . import callback
from . import logger, DEVICE_ID


def main():
    url = os.environ.get('MQTT_BROKER_URL', 'mqtt://localhost:1883')  # type: str
    connection = urlparse(url)  # type: ParseResult

    client = mqtt.Client(client_id='tv-controller_{}-{}'.format(DEVICE_ID, uuid.uuid4()), clean_session=True, userdata=None, transport='tcp')
    client.username_pw_set(connection.username, connection.password)
    if connection.scheme == "mqtts":
        client.tls_set()

    client.on_connect = callback.on_mqtt_connect
    client.on_disconnect = callback.on_mqtt_dicconnect
    client.on_message = callback.on_mqtt_message

    client.connect(connection.hostname, connection.port)

    logger.debug('main started with sys args: %s', str(sys.argv))
    client.loop_forever()


if __name__ == '__main__':
    main()
