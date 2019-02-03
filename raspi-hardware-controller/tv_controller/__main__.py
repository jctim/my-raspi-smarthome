import os
import sys

from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

from .__init__ import logger
from .callback import AlexaCloudCallback


def main():
    pnconfig = PNConfiguration()
    pnconfig.publish_key = os.environ.get('PUBNUB_PUB_KEY', '')
    pnconfig.subscribe_key = os.environ.get('PUBNUB_SUB_KEY', '')
    pnconfig.ssl = True
    pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR

    pubnub = PubNub(pnconfig)
    pubnub.add_listener(AlexaCloudCallback())
    pubnub.subscribe().channels('alexa').with_presence().execute()

    logger.debug('main started with sys args: {}'.format(sys.argv))


if __name__ == '__main__':
    main()
