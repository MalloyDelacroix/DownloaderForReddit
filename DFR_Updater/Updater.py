import requests
import os
import sys
import shutil
import tempfile
import zipfile
from PyQt5.QtCore import QObject, QSettings, pyqtSignal

source_location = 'C:\\Users\\Kyle\\Documents\\Programming\\TestDownloadFolder\\DownloaderForReddit'


class Updater(QObject):

    finished = pyqtSignal()
    set_label = pyqtSignal(str)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar = pyqtSignal(int)

    def __init__(self, download_url, download_name, new_version, program_files_location):
        super().__init__()
        self.download_url = download_url
        self.download_name = download_name
        self.new_version = new_version
        # self.program_files_location = program_files_location

        self.program_files_location = source_location
        self.platform = sys.platform
        self.suffix = '.tar.gz' if self.platform == 'linux' else '.zip'
        self.temp_directory = tempfile.mkdtemp()
        self.file_name = os.path.join(self.temp_directory, self.download_name)

        print(self.download_url)
        print(self.new_version)
        print(self.program_files_location)

    def run(self):
        pass

    def download_update(self):
        download = requests.get(self.download_url, stream=True)
        if download.status_code == 200:
            download_size = download.headers.get('content-length')
            self.setup_progress_bar.emit(int(download_size))
            with open(self.file_name, 'wb') as file:
                for chunk in download.iter_content(1024):
                    file.write(chunk)
                    self.update_progress_bar.emit(len(chunk))
            print('download complete')

    def delete_old_files(self):
        if 'DownloaderForReddit.exe' in os.listdir(self.program_files_location):
            for item in os.listdir(self.program_files_location):
                if os.path.isfile(os.path.join(self.program_files_location, item)):
                    os.remove(os.path.join(self.program_files_location, item))
                else:
                    shutil.rmtree(os.path.join(self.program_files_location, item))

    def replace_with_new_version(self):
        zip_ref = zipfile.ZipFile(self.file_name, 'r')
        zip_ref.extractall(self.temp_directory)
        zip_ref.close()

        unpacked_directory = None
        for x in os.listdir(self.temp_directory):
            if x != self.file_name:
                unpacked_directory = os.path.join(self.temp_directory, x)

        if unpacked_directory is not None:
            for file in os.listdir(unpacked_directory):
                shutil.move(os.path.join(unpacked_directory, file), self.program_files_location)

    def clean_up_temporary(self):
        shutil.rmtree(self.temp_directory)

    def stop(self):
        pass
