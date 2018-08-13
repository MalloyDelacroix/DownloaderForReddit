"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

from ..Utils import SystemUtil
from ..Logging.StreamFormatter import JsonStreamFormatter


def make_logger():
    logger = logging.getLogger('DownloaderForReddit')
    logger.setLevel(logging.DEBUG)

    stream_formatter = JsonStreamFormatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s',
                                           datefmt='%m/%d/%Y %I:%M:%S %p')

    json_formatter = jsonlogger.JsonFormatter(fmt='%(levelname) %(name) %(filename) %(module) %(funcName) %(lineno) '
                                              '%(message) %(asctime)', datefmt='%m/%d/%Y %I:%M:%S %p')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(stream_formatter)

    log_path = os.path.join(SystemUtil.get_data_directory(), 'DownloaderForReddit.log')
    file_handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=2)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
