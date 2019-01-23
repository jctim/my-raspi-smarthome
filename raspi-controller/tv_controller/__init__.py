import logging

DEVICE_ID = 'tv-01'

FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
