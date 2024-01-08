import logging

logger = logging.getLogger('WEB')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
logging.getLogger().setLevel(logging.WARNING)
