
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
from queue import Queue
from PyQt5 import QtWidgets, QtCore

from GUI.DownloaderForRedditGUI import DownloaderForRedditGUI
from version import __version__

# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#   QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if sys.platform == 'win32':
    myappid = 'SomeGuySoftware.DownloaderForReddit.%s' % __version__
    AppUserModelID = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MessageReceiver(QtCore.QObject):

    output_signal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, queue, *args, **kwargs):
        """
        A class monitors the supplied instance of the queue that is common throughout all parts of the program which
        emits a signal to update the main GUI window when something comes through the queue.  This class will be moved
        operate from another thread

        This concept is taken directly from NSchrading's application "redditDataExtractor" which much of this
        application is based on.  This is a brilliant way to solve many problems involved in sending messages between
        parts of the application which are operating in different threads.

        :param queue: An instance of the queue supplied in the "main" function
        """
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.continue_run = True

    def run(self):
        while self.continue_run:
            output = self.queue.get()
            self.output_signal.emit(output)
        self.finished.emit()

    def stop_run(self):
        """
        Stops the receiver from running which allows threads to end cleanly.  '' is added to the queue because it will
        block until it receives something
        """
        self.continue_run = False
        self.queue.put('')


def main():
    app = QtWidgets.QApplication(sys.argv)

    queue = Queue()
    thread = QtCore.QThread()
    receiver = MessageReceiver(queue)

    window = DownloaderForRedditGUI(queue, receiver)

    receiver.output_signal.connect(window.update_output)
    receiver.moveToThread(thread)
    thread.started.connect(receiver.run)
    receiver.finished.connect(thread.quit)
    receiver.finished.connect(receiver.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
