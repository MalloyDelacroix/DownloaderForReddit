
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


import ctypes
import sys
from PyQt5 import QtWidgets, QtCore
import logging

from DownloaderForReddit.gui.downloader_for_reddit_gui import DownloaderForRedditGUI
from DownloaderForReddit.messaging.message_receiver import MessageReceiver
from DownloaderForReddit.utils import injector
from DownloaderForReddit.local_logging import logger
from DownloaderForReddit.version import __version__

# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#   QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if sys.platform == 'win32':
    myappid = 'SomeGuySoftware.DownloaderForReddit.%s' % __version__
    AppUserModelID = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def log_unhandled_exception(exc_type, value, traceback):
    logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
    logger.critical('Unhandled exception', exc_info=(exc_type, value, traceback))
    sys.exit(-1)


def main():
    logger.make_logger()
    sys.excepthook = log_unhandled_exception

    app = QtWidgets.QApplication(sys.argv)

    queue = injector.get_message_queue()
    message_thread = QtCore.QThread()
    receiver = MessageReceiver(queue)
    scheduler = injector.get_scheduler()

    window = DownloaderForRedditGUI(queue, receiver, scheduler)

    receiver.text_output.connect(window.update_output)
    receiver.potential_extraction.connect(window.handle_potential_extraction)
    receiver.actual_extraction.connect(window.handle_extraction)
    receiver.potential_download.connect(window.handle_potential_download)
    receiver.actual_download.connect(window.handle_download)
    receiver.extraction_error.connect(window.handle_extraction_error)
    receiver.download_error.connect(window.handle_download_error)

    receiver.moveToThread(message_thread)
    message_thread.started.connect(receiver.run)
    receiver.finished.connect(message_thread.quit)
    receiver.finished.connect(receiver.deleteLater)
    message_thread.finished.connect(message_thread.deleteLater)
    message_thread.start()

    schedule_thread = QtCore.QThread()
    scheduler.moveToThread(schedule_thread)
    scheduler.run_task.connect(window.run_scheduled_download)
    scheduler.countdown.connect(window.update_scheduled_download)
    scheduler.finished.connect(schedule_thread.quit)
    scheduler.finished.connect(scheduler.deleteLater)
    schedule_thread.finished.connect(schedule_thread.deleteLater)
    schedule_thread.started.connect(scheduler.run)
    schedule_thread.start()

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
