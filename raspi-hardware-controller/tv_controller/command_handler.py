import json
import os
from typing import Dict, List, Tuple, Union

import paho.mqtt.client as mqtt  # type: ignore
import requests

from . import ALEXA_REPLY_TOPIC, CEC_CMD, HDMI_NAMES, TV_API_URL, TX_CMD
from . import logger, str_to_bool


# TODO think about how to deploy on RPI.

def handle_control_command(command: Dict[str, str], client: mqtt.Client) -> None:
    """
    supported commands:
        * power control: {"power": "on|off"}
        * source (input) switch : {"source": "<input name>"},
            where <input name> is a value from HDMI_NAMES
        * volume control: {"volume": "<int value>|yes|true|no|false" "type": "abs|rel|mute"},
            where <int value> may be used with types 'abs' and 'rel'
            but 'yes', 'true', 'no', 'false' may be used only with type 'mute'

    each command also should contain "uuid" key

    :param command:
    :param client:
    :return:
    """
    logger.debug("Received command %s", command)
    if 'uuid' not in command:
        logger.debug('...but there is no "uuid" in command, skipping it')
        return

    uuid = command['uuid']
    if 'power' in command:
        logger.debug('tv power will be %s', command['power'])
        handle_power(command['power'], client=client, uuid=uuid)
    elif 'source' in command:
        logger.debug('tv source will be %s', command['source'].upper())
        handle_source(command['source'].upper(), client=client, uuid=uuid)
    elif 'volume' in command and 'type' in command:
        logger.debug('tv volume (type=%s) will be %s', command['type'], command['volume'])
        handle_volume(command['type'], command['volume'], client=client, uuid=uuid)
    else:
        logger.debug('...but it\'s unsupported command')
        _reply_with_error("unsupported command", client=client, uuid=uuid)


def handle_power(value: str, **kwargs) -> None:
    if value == 'on' or value == 'off':
        _exec_cec_cmd(TX_CMD['power'][value])
        _reply_with_values({"power": value}, **kwargs)
    else:
        logger.debug('Unknown power value: %s', value)
        _reply_with_error("unknown power value", **kwargs)


def handle_source(value: str, **kwargs) -> None:
    matched_source = [hdmi for hdmi, names in HDMI_NAMES.items() if value in names]
    if len(matched_source) == 1:
        _exec_cec_cmd(TX_CMD['source'][matched_source[0]])
        _reply_with_values({"source": value}, **kwargs)
    else:
        logger.debug('Unknown source: %s', value)
        _reply_with_error("unknown source", **kwargs)


def handle_volume(volume_type: str, volume_value: str, **kwargs) -> None:
    api_volume = _get_api_volume()
    if api_volume is None:
        logger.debug('Cannot get current volume. Looks like TV API is unreachable')
        _reply_with_error("an error occurred during executing operation", **kwargs)
        return

    (muted, current_volume, max_volume) = api_volume

    if volume_type == 'abs':
        new_value = min(int(volume_value), max_volume)
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"current": new_value})
        if r.status_code == 200:
            _reply_with_values({"muted": str(muted).lower(), "volume": new_value})
        else:
            logger.debug('Unsuccessful operation: %d', r.status_code)
            _reply_with_error("an error occurred during executing operation")

    elif volume_type == 'rel':
        new_value = max(1, min(current_volume + int(volume_value), max_volume))
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"current": new_value})
        if r.status_code == 200:
            _reply_with_values({"muted": str(muted).lower(), "volume": new_value})
        else:
            logger.debug('Unsuccessful operation: %d', r.status_code)
            _reply_with_error("an error occurred during executing operation")

    elif volume_type == 'mute':
        new_value = str_to_bool(volume_value)
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"muted": new_value})
        if r.status_code == 200:
            _reply_with_values({"muted": str(new_value).lower(), "volume": current_volume})
        else:
            logger.debug('Unsuccessful operation: %d', r.status_code)
            _reply_with_error("an error occurred during executing operation")

    else:
        logger.debug('Unknown volume type: %s', volume_type)
        _reply_with_error("unknown volume type")


def _exec_cec_cmd(tx_cmd: List[str]) -> None:
    logger.debug('sending CEC command(s) %s...', tx_cmd)
    try:
        [os.system(CEC_CMD.format(cmd)) for cmd in tx_cmd]
        logger.debug('sent!')
    except OSError as err:
        logger.error('Cannot execute CEC command(s) %s: %s', tx_cmd, err)


def _get_api_volume() -> Union[Tuple[bool, int, int], None]:
    try:
        r = requests.get(TV_API_URL.format(cmd='audio/volume'), timeout=1)
        if r.status_code == 200:
            r_json = r.json()
            current_muted = bool(r_json['muted'])
            current_volume = int(r_json['current'])
            max_volume = int(r_json['max'])
            return current_muted, current_volume, max_volume
    except requests.exceptions.Timeout:
        logger.warn("TV API didn't response in 1 sec")

    return None


def _reply_with_values(values: Dict[str, Union[str, int]], **kwargs) -> mqtt.MQTTMessageInfo:  # client: mqtt.Client, uuid: str
    client: mqtt.Client = kwargs.get('client')
    if client is not None:
        uuid = kwargs['uuid']
        qos = int(kwargs.get('qos') or 1)
        return client.publish(ALEXA_REPLY_TOPIC, json.dumps(dict({"uuid": uuid}, **values)), qos)


def _reply_with_error(error_desc: str, **kwargs) -> mqtt.MQTTMessageInfo:  # client: mqtt.Client, uuid: str
    client: mqtt.Client = kwargs.get('client')
    if client is not None:
        uuid = kwargs['uuid']
        qos = int(kwargs.get('qos') or 1)
        return client.publish(ALEXA_REPLY_TOPIC, json.dumps({"uuid": uuid, "error": error_desc}), qos)
