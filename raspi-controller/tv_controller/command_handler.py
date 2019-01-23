#! /usr/bin/env python3

import os
import subprocess
import sys

from .__init__ import logger

# TODO think about how to deploy on RPI.

def handle_control_command(controlCommand):
    logger.debug(controlCommand)
    if 'power' in controlCommand:
        logger.debug('tv will ' + controlCommand['power'])
        _power(controlCommand['power'])
    elif 'source' in controlCommand:
        logger.debug('tv source will ' + controlCommand['source'])
        _source(controlCommand['source'])
    else:
        logger.debug('unsupported command')

def _power(action):
    try:
        logger.debug('sending CEC command...')
        if action == 'on':
            os.system('echo "tx 10:04" | cec-client RPI -s -d 1')
        elif action == 'off':
            os.system('echo "tx 10:36" | cec-client RPI -s -d 1')
        logger.debug('sent!')
    except OSError as err:
        logger.error('Cannot execute CEC command for action="{}". '.format(action), err)

def _source(source):
    try:
        logger.debug('sending key code...')
        if source == 'ANDROID' or source == 'ANDROID TV' or source == 'MIBOX' or source == 'HDMI 1':
            os.system('echo "tx 1F:82:10:00" | cec-client RPI -s -d 1')
            os.system('echo "tx 1F:86:10:00" | cec-client RPI -s -d 1')
        elif source == 'XBOX' or source == 'HDMI 2':
            os.system('echo "tx 1F:82:20:00" | cec-client RPI -s -d 1')
            os.system('echo "tx 1F:86:20:00" | cec-client RPI -s -d 1')
        elif source == 'APPLE' or source == 'APPLE TV' or source == 'HDMI 3':
            os.system('echo "tx 1F:82:30:00" | cec-client RPI -s -d 1')
            os.system('echo "tx 1F:86:30:00" | cec-client RPI -s -d 1')
        elif source == 'RASPBERRY' or source == 'CONTROLLER' or source == 'HDMI 4':
            os.system('echo "tx 1F:82:40:00" | cec-client RPI -s -d 1')
            os.system('echo "tx 1F:86:40:00" | cec-client RPI -s -d 1')
        else:
            logger.debug('Unknown source: ' + source)
        logger.debug('sent!')
    except OSError as err:
        logger.error('Cannot execute CEC command for action="{}". '.format(source), err)
