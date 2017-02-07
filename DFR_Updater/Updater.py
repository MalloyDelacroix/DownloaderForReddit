import requests
import os
import sys
import shutil
import tempfile
import zipfile
from PyQt5.QtCore import QObject, pyqtSignal

# source_location = 'C:\\Users\\Kyle\\Documents\\Programming\\TestDownloadFolder\\DownloaderForReddit'


class Updater(QObject):

    finished = pyqtSignal()
    update_label = pyqtSignal(str)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar = pyqtSignal(int)
    error_signal = pyqtSignal(tuple)

    def __init__(self, download_url, download_name, new_version, program_files_location):
        super().__init__()
        self.download_url = download_url
        self.download_name = download_name
        self.new_version = new_version
        self.program_files_location = program_files_location

        # self.program_files_location = source_location
        self.platform = sys.platform
        self.suffix = '.tar.gz' if self.platform == 'linux' else '.zip'
        self.temp_directory = tempfile.mkdtemp()
        self.file_name = os.path.join(self.temp_directory, self.download_name)

        self.run = True

    def run_update(self):
        self.run = True
        self.download_update()
        self.delete_old_files()
        self.replace_with_new_version()
        self.clean_up_temporary()
        self.finished.emit()

    def download_update(self):
        if self.run:
            self.update_label.emit('Establishing connection...')
            download = requests.get(self.download_url, stream=True)
            if download.status_code == 200:
                self.update_label.emit('Downloading new update...')
                download_size = download.headers.get('content-length')
                self.setup_progress_bar.emit(int(download_size))
                with open(self.file_name, 'wb') as file:
                    if self.run:
                        for chunk in download.iter_content(1024):
                            file.write(chunk)
                            self.update_progress_bar.emit(len(chunk))
                self.update_label.emit('Download Complete')
            else:
                self.run = False
                self.error_signal.emit((0, 0))

    def delete_old_files(self):
        self.update_label.emit('Removing outdated program files...')
        if 'praw.ini' in os.listdir(self.program_files_location):
            if self.run:
                file_list = os.listdir(self.program_files_location)
                self.setup_progress_bar.emit(len(file_list))
                for item in file_list:
                    if self.run:
                        if os.path.isfile(os.path.join(self.program_files_location, item)) and not \
                                item.startswith('save'):
                            os.remove(os.path.join(self.program_files_location, item))
                            self.update_progress_bar.emit(1)
                        elif os.path.isdir(os.path.join(self.program_files_location, item))and not\
                                item.lower().startswith('dfr'):
                            shutil.rmtree(os.path.join(self.program_files_location, item))
                            self.update_progress_bar.emit(1)
        else:
            self.run = False
            self.error_signal.emit((1, self.temp_directory))

    def replace_with_new_version(self):
        try:
            if self.run:
                self.update_label.emit('Installing new update...')
                zip_ref = zipfile.ZipFile(self.file_name, 'r')
                zip_ref.extractall(self.temp_directory)
                zip_ref.close()

                unpacked_directory = None
                for x in os.listdir(self.temp_directory):
                    if x != self.file_name:
                        unpacked_directory = os.path.join(self.temp_directory, x)

                if unpacked_directory is not None and self.run:
                    file_list = os.listdir(unpacked_directory)
                    self.setup_progress_bar.emit(len(file_list))
                    for file in file_list:
                        shutil.move(os.path.join(unpacked_directory, file), self.program_files_location)
                        self.update_progress_bar.emit(1)
        except:
            self.error_signal.emit((2, self.temp_directory))

    def clean_up_temporary(self):
        self.update_label.emit('Cleaning up temp folder...')
        shutil.rmtree(self.temp_directory)

    def stop(self):
        self.run = False
        self.update_label.emit('Updater stopped')
