from pubnub.callbacks import SubscribeCallback

from . import logger, DEVICE_ID
from .command_handler import handle_control_command

class CloudCallback(SubscribeCallback):

    def status(self, pubnub, status):
        logger.debug('status: {}'.format(status))

    def presence(self, pubnub, presence):
        logger.debug('presence: {}'.format(presence))

    def message(self, pubnub, message):
        logger.debug('message: {}'.format(message.message))
        command = message.message
        if ('requester' in command and command['requester'] == 'Alexa'
            and 'device' in command and command['device'] == DEVICE_ID):
                handle_control_command(command)

