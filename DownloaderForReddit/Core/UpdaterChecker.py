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


import requests
import sys
from PyQt5.QtCore import QObject, pyqtSignal


class UpdateChecker(QObject):

    update_available_signal = pyqtSignal(str)
    no_update_signal = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, installed_version):
        """
        Class that runs on a separate thread from the main GUI and checks github for a newly released version of the
        program.
        :param installed_version: The version of the application that is currently installed
        """
        super().__init__()
        self.installed_version = installed_version
        self.release_api_caller = 'https://api.github.com/repos/MalloyDelacroix/DownloaderForReddit/releases/latest'
        self._json = None
        self.download_type = 'zip' if sys.platform != 'linux' else 'tar.gz'
        self.newest_version = None
        self.download_size = None
        self.download_url = None
        self.download_name = None

    def run(self):
        try:
            self.retrieve_json_data()
            self.check_releases()
        except:
            print('Update checker failed to establish a connection')
        finally:
            self.finished.emit()

    def retrieve_json_data(self):
        response = requests.get(self.release_api_caller)
        if response.status_code == 200:
            self._json = response.json()
        else:
            print('Failed connection: %s' % response.status_code)

    def check_releases(self):
        """
        Checks the json content retrieved from github to see if there is an update available and information about it
        """
        if self._json['tag_name'] != self.installed_version:
            self.newest_version = self._json['tag_name']
            for asset in self._json['assets']:
                if asset['name'].endswith(self.download_type):
                    self.download_name = asset['name']
                    self.download_size = asset['size']
                    self.download_url = asset['browser_download_url']
                    self.update_available_signal.emit(self.newest_version)
        else:
            self.no_update_signal.emit()
