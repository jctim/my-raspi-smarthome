#! /usr/bin/env python3

import os
from typing import Dict, List, Tuple, Union

import requests
from pubnub.pubnub import PubNub

from . import CEC_CMD, HDMI_NAMES, TV_API_URL, TX_CMD, DEVICE_ID, logger, str_to_bool


# TODO think about how to deploy on RPI.


def exec_cec_cmd(tx_cmd: List[str]) -> None:
    logger.debug('sending CEC command(s) {}...'.format(tx_cmd))
    try:
        [os.system(CEC_CMD.format(cmd)) for cmd in tx_cmd]
        logger.debug('sent!')
    except OSError as err:
        logger.error('Cannot execute CEC command(s) {}'.format(tx_cmd), err)


def handle_power(action: str) -> None:
    if action == 'on' or action == 'off':
        exec_cec_cmd(TX_CMD['power'][action])
    else:
        logger.debug('Unknown power action: {}'.format(action))


def handle_source(source: str) -> None:
    matched_source = [hdmi for hdmi, names in HDMI_NAMES.items() if source in names]
    if len(matched_source) == 1:
        exec_cec_cmd(TX_CMD['source'][matched_source[0]])
    else:
        logger.debug('Unknown source: {}'.format(source))


def _get_api_volume() -> Union[Tuple[bool, int, int], None]:
    r = requests.get(TV_API_URL.format(cmd='audio/volume'))
    if r.status_code == 200:
        rjson = r.json()
        current_muted = bool(rjson['muted'])
        current_volume = int(rjson['current'])
        max_volume = int(rjson['max'])
        return current_muted, current_volume, max_volume

    return None


def handle_volume(volume_type: str, volume_value: str, pubnub: PubNub) -> None:
    api_volume = _get_api_volume()
    if api_volume is None:
        logger.debug('Cannot get current volume. Looks like TV API is unaccessible')
        return

    (muted, current_volume, max_volume) = api_volume

    if volume_type == 'abs':
        new_value = min(int(volume_value), max_volume)
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"current": new_value})
        if r.status_code == 200:
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "muted": str(muted).lower(),
                "volume": new_value
            }).sync()
        else:
            logger.debug('Unsuccessful operation: {}'.format(r.status_code))
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "error": "an error occurred during executing operation"
            }).sync()

    elif volume_type == 'rel':
        new_value = max(1, min(current_volume + int(volume_value), max_volume))
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"current": new_value})
        if r.status_code == 200:
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "muted": str(muted).lower(),
                "volume": new_value
            }).sync()
        else:
            logger.debug('Unsuccessful operation: {}'.format(r.status_code))
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "error": "an error occurred during executing operation"
            }).sync()

    elif volume_type == 'mute':
        new_value = str_to_bool(volume_value)
        r = requests.post(TV_API_URL.format(cmd='audio/volume'), json={"muted": new_value})
        if r.status_code == 200:
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "muted": str(new_value).lower(),
                "volume": current_volume
            }).sync()
        else:
            logger.debug('Unsuccessful operation: {}'.format(r.status_code))
            pubnub.publish().channel('alexa_response').message({
                "requester": "Device",
                "device": DEVICE_ID,
                "error": "an error occurred during executing operation"
            }).sync()

    else:
        logger.debug('Unknown volume type: {}'.format(volume_type))


def handle_control_command(command: Dict[str, str], pubnub: PubNub) -> None:
    if 'power' in command:
        logger.debug('tv power will {}'.format(command['power']))
        handle_power(command['power'])
    elif 'source' in command:
        logger.debug('tv source will {}'.format(command['source']))
        handle_source(command['source'])
    elif 'volume' in command and 'type' in command:
        logger.debug('tv volume (type={}) will {}'.format(command['type'], command['volume']))
        handle_volume(command['type'], command['volume'], pubnub)
    else:
        logger.debug('unsupported command {}'.format(command))
