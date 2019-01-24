#! /usr/bin/env python3

import os
import subprocess
import sys
from typing import Any, Dict, List

from .__init__ import logger

# TODO think about how to deploy on RPI.


# Refer to https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=53481
CEC_CMD = 'echo "{}" | cec-client RPI -s -d 1'

# Refer to http://www.cec-o-matic.com
TX_CMD: Dict[str, Dict[str, List[str]]] = {
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

HDMI_NAMES: Dict[str, List[str]] = {
    'hdmi1': ['HDMI 1', 'ANDROID', 'ANDROID TV', 'MIBOX'],
    'hdmi2': ['HDMI 2', 'XBOX'],
    'hdmi3': ['HDMI 3', 'APPLE', 'APPLE TV'],
    'hdmi4': ['HDMI 4', 'RASPBERRY', 'RASPBERRY PI', 'CONTROLLER']
}


def handle_control_command(command: Dict[str, str]) -> None:
    if 'power' in command:
        logger.debug('tv power will {}'.format(command['power']))
        _power(command['power'])
    elif 'source' in command:
        logger.debug('tv source will {}'.format(command['source']))
        _source(command['source'])
    else:
        logger.debug('unsupported command {}'.format(command))


def _power(action: str) -> None:
    if action == 'on' or action == 'off':
        _exec_cec(TX_CMD['power'][action])
    else:
        logger.debug('Unknown power action: {}'.format(action))


def _source(source: str) -> None:
    matched_source = [hdmi for hdmi, names in HDMI_NAMES.items() if source in names]
    if len(matched_source) == 1:
        _exec_cec(TX_CMD['source'][matched_source[0]])
    else:
        logger.debug('Unknown source: {}'.format(source))


def _exec_cec(tx_cmd: List[str]) -> None:
    logger.debug('sending CEC command(s) {}...'.format(tx_cmd))
    try:
        # [print(CEC_CMD.format(cmd)) for cmd in tx_cmd]
        [os.system(CEC_CMD.format(cmd)) for cmd in tx_cmd]
        logger.debug('sent!')
    except OSError as err:
        logger.error('Cannot execute CEC command(s) {}'.format(tx_cmd), err)
