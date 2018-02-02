import os
import logging


def make_logger():
    logger = logging.getLogger('DownloaderForReddit')
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s :  %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)

    logger.info('Logger created')
