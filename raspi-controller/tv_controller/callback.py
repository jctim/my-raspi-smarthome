from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.models.consumer.common import PNStatus
from pubnub.models.consumer.pubsub import (PNMessageResult,
                                           PNPresenceEventResult)
from pubnub.pubnub import PubNub

from .__init__ import DEVICE_ID, logger
from .command_handler import handle_control_command


class AlexaCloudCallback(SubscribeCallback):

    def status(self, pubnub: PubNub, status: PNStatus) -> None:
        logger.debug('status: {}'.format(vars(status)))
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pubnub.reconnect()
        elif status.category == PNStatusCategory.PNTimeoutCategory:
            pubnub.reconnect()

    def presence(self, pubnub: PubNub, presence: PNPresenceEventResult) -> None:
        logger.debug('presence: {}'.format(vars(presence)))

    def message(self, pubnub: PubNub, message: PNMessageResult) -> None:
        logger.debug('message: {}'.format(vars(message)))

        if message.channel != 'alexa':
            return

        command = message.message
        if ('requester' in command and command['requester'] == 'Alexa'
                and 'device' in command and command['device'] == DEVICE_ID):
            handle_control_command(command, pubnub)
