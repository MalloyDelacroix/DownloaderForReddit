import os
import logging
from pythonjsonlogger import jsonlogger
import sys

from Core import SystemUtil


def make_logger():
    logger = logging.getLogger('DownloaderForReddit')
    logger.setLevel(logging.DEBUG)

    stream_formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s',
                                               datefmt='%m/%d/%Y %I:%M:%S %p')

    json_formatter = jsonlogger.JsonFormatter(fmt='%(levelname) %(name) %(filename) %(module) %(funcName) %(lineno) '
                                              '%(message) %(asctime)', datefmt='%m/%d/%Y %I:%M:%S %p')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(json_formatter)

    log_path = os.path.join(SystemUtil.get_data_directory(), 'DownloaderForReddit.log')
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
