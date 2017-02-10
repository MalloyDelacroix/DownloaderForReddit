import requests
import os
import sys
from PyQt5.QtCore import QObject, QSettings, pyqtSignal


class UpdateChecker(QObject):

    update_available_signal = pyqtSignal(tuple)
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
        self.retrieve_json_data()
        self.check_releases()
        self.finished.emit()

    def retrieve_json_data(self):
        response = requests.get(self.release_api_caller)
        if response.status_code == 200:
            self._json = response.json()

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
                    self.update_available_signal.emit((self.newest_version, self.download_size))
                    self.save_download_url()
        else:
            self.no_update_signal.emit()

    def save_download_url(self):
        """
        These variables are saved and then used by the updater application so it does not have to make the same call to
        the github api to retrieve the same information as above
        """
        settings = QSettings('SomeGuySoftware', 'dfr_updater')
        settings.setValue('download_url', self.download_url)
        settings.setValue('download_name', self.download_name)
        settings.setValue('new_version', self.newest_version)
        settings.setValue('program_files_location', os.getcwd())
