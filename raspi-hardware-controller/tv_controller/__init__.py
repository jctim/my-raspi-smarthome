import logging
import os

# MQTT Broker URL
MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL', 'mqtt://localhost:1883')
# User scope - a unique string (uuid is good choice) that represents current user
MQTT_USER_SCOPE = os.environ.get('MQTT_USER_SCOPE', '_dev_scope_')
# Device id - is used as endpoint_id in cloud_controller
DEVICE_ID = os.environ.get('DEVICE_TV_ID', 'tv-01')
# Device IP - the IP address to be used to make REST calls (see below)
DEVICE_IP = os.environ.get('DEVICE_TV_IP', '192.168.1.97')

# API URL used to make REST calls to JointSpace API of the TV
TV_API_URL = 'http://{ip}:1925/1/{cmd}'.format(ip=DEVICE_IP, cmd='{cmd}')

# MQTT topics
ALEXA_CONTROL_TOPIC = 'alexa/{}/device/{}/control'.format(MQTT_USER_SCOPE, DEVICE_ID)
ALEXA_REPLY_TOPIC = 'alexa/{}/device/{}/reply'.format(MQTT_USER_SCOPE, DEVICE_ID)

# Refer to https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=53481
CEC_CMD = 'echo "{}" | cec-client RPI -s -d 1'

# Refer to http://www.cec-o-matic.com
TX_CMD = {
    'power': {
        'on': ['tx 10:04'],
        'off': ['tx 10:36']
    },
    'source': {
        'hdmi1': ['tx 1F:82:10:00', 'tx 1F:86:10:00'],
        'hdmi2': ['tx 1F:82:20:00', 'tx 1F:86:20:00'],
        'hdmi3': ['tx 1F:82:30:00', 'tx 1F:86:30:00'],
        'hdmi4': ['tx 1F:82:40:00', 'tx 1F:86:40:00']
    }
}

HDMI_NAMES = {
    'hdmi1': ['HDMI 1', 'ANDROID', 'ANDROID TV', 'MIBOX'],
    'hdmi2': ['HDMI 2', 'XBOX'],
    'hdmi3': ['HDMI 3', 'APPLE', 'APPLE TV'],
    'hdmi4': ['HDMI 4', 'RASPBERRY', 'RASPBERRY PI', 'CONTROLLER']
}

FORMAT = '%(asctime)-15s %(message)s'

# Logger config
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def str_to_bool(s: str) -> bool:
    return s.lower() in ('yes', 'true', '1')
