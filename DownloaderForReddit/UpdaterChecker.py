import requests
import shutil
import os
import sys
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QSettings, pyqtSignal


class UpdateChecker(QObject):

    update_available_signal = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, installed_version):
        super().__init__()
        print('UpdateChecker initialized')
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
        print('retrieving json')
        response = requests.get(self.release_api_caller)
        if response.status_code == 200:
            self._json = response.json()

    def check_releases(self):
        print('checking releases')
        if self._json['tag_name'] != self.installed_version:
            self.newest_version = self._json['tag_name']
            for asset in self._json['assets']:
                if asset['name'].endswith(self.download_type):
                    self.download_name = asset['name']
                    self.download_size = asset['size']
                    self.download_url = asset['browser_download_url']
                    self.update_available_signal.emit((self.newest_version, self.download_size))
                    self.save_download_url()

    def save_download_url(self):
        print('information saved')
        settings = QSettings('SomeGuySoftware', 'dfr_updater')
        settings.setValue('download_url', self.download_url)
        settings.setValue('download_name', self.download_name)
        settings.setValue('new_version', self.newest_version)
        settings.setValue('program_files_location', os.getcwd())





"""
Test work:

def download_latest_release():
    api = 'https://api.github.com/'
    response = requests.get(api + 'repos/MalloyDelacroix/DownloaderForReddit/releases/latest')

    if response.status_code == 200:
        r = response.json()
        version = r['tag_name']
        id = r['id']
        assets_list = r['assets']
        print(id)
        print(version)
        print('\nasset:\n')

        for x in assets_list:
            if x['content_type'] == 'application/x-compressed':
                print('New Download')
                download_url = x['browser_download_url']
                filename = 'C:path_to_folder/%s' % x['name']
                download = requests.get(download_url, stream=True)
                if download.status_code == 200:
                    with open(filename, 'wb') as file:
                        for chunk in download.iter_content(1024):
                            file.write(chunk)
                    print('download complete')

"""




