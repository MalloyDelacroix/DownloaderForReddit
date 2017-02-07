import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtCore

from UpdaterGUI_auto import Ui_updater_gui
from Updater import Updater


class UpdaterWidget(QtWidgets.QWidget, Ui_updater_gui):

    cancel_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.settings = QtCore.QSettings('SomeGuySoftware', 'dfr_updater')
        self.restoreGeometry(self.settings.value('geometry', self.saveGeometry()))
        self.download_url = self.settings.value('download_url', None, type=str)
        self.download_name = self.settings.value('download_name', None, type=str)
        self.new_version = self.settings.value('new_version', None, type=str)
        self.launch_checkbox.setChecked(self.settings.value('launch_checkbox', False, type=bool))
        self.save_height = True
        self.label.setOpenExternalLinks(True)
        self.program_files_location = self.settings.value('program_files_location', None, type=str)
        self.running = False
        self.up_to_date = False

        if self.up_to_date:
            self.button_box.accepted.connect(self.open_file_location)
        else:
            self.button_box.accepted.connect(self.run)
        if self.running:
            self.button_box.rejected.connect(self.stop_download())
        else:
            self.button_box.rejected.connect(self.close)

        self.progress_bar.setVisible(False)
        self.launch_checkbox.setVisible(False)

    def run(self):
        self.update_label('Starting updater...')
        self.running_gui_shift()

        self.thread = QtCore.QThread()
        self.updater = Updater(self.download_url, self.download_name, self.new_version, None)
        self.cancel_signal.connect(self.updater.stop)
        self.updater.moveToThread(self.thread)
        self.thread.started.connect(self.updater.run_update)
        self.updater.update_label.connect(self.update_label)
        self.updater.setup_progress_bar.connect(self.setup_progress_bar)
        self.updater.update_progress_bar.connect(self.update_progress_bar)
        self.updater.error_signal.connect(self.update_error)
        self.updater.finished.connect(self.thread.quit)
        self.updater.finished.connect(self.updater.deleteLater)
        self.updater.finished.connect(self.finished_gui_shift)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def running_gui_shift(self):
        self.progress_bar.setVisible(True)
        self.running = True
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Stop')

    def finished_gui_shift(self):
        self.running = False
        self.up_to_date = True
        self.update_label('Update complete. You are now running the latest version.')
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText('Open exe location')
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')
        self.launch_checkbox.setVisible(True)

    def stopped_gui_shift(self):
        self.running = False
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(True)
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')

    def update_label(self, text):
        self.label.setText(text)

    def setup_progress_bar(self, setup):
        if setup > 100:
            minimum = 0 - (setup - 100)
            maximum = 100
        else:
            minimum = 0
            maximum = setup
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(minimum)

    def update_progress_bar(self, length):
        self.progress_bar.setValue(self.progress_bar.value() + length)

    def stop_download(self):
        self.cancel_signal.emit()
        self.finished_gui_shift()

    def open_file_location(self):
        if sys.platform == 'win32':
            os.startfile(self.program_files_location)
        else:
            subprocess.call(['xdg-open', self.program_files_location])

    def launch_program(self):
        if sys.platform == 'win32':
            os.startfile(os.path.join(self.program_files_location, 'DownloaderForReddit.exe'))
        elif sys.platform == 'linux':
            subprocess.call(['xdg-open', os.path.join(self.program_files_location, 'DownloaderForReddit')])

    def update_error(self, code):
        self.stopped_gui_shift()
        if code[0] == 0:
            self.update_label('There was a problem establishing a connection to the github download url.  Please try '
                              'the update again.  If the problem persists the package can be downloaded manually at: '
                              '<a href="https://github.com/MalloyDelacroix/DownloaderForReddit/releases">https://github.com/MalloyDelacroix/DownloaderForReddit/releases</a>')
            self.setMinimumHeight(self.height() + self.label.height())
            self.save_height = False

        elif code[0] == 1:
            self.update_label('There was a problem deleting the outdated files. There was no Downloader for Reddit '
                              'executable found in the folder location. Please try the update again. If the '
                              'problem persists, the latest update has been downloaded at can be moved manually to '
                              'the desired location.')
            self.setMinimumHeight(self.height() + self.label.height())
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText('Open Download Location')
            self.button_box.accepted.connect(lambda: self.open_temporary_download_location(code[1]))
            self.save_height = False
        elif code[0] == 2:
            self.update_label('There was a problem extracting or moving the downloaded files to the programs directory '
                              'The original program files have been removed.  You may manually move the downloaded '
                              'files to the desired location and run the Downloader for Reddit from there.')
            self.setMinimumHeight(self.height() + self.label.height())
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText('Open Download Location')
            self.button_box.accepted.connect(lambda: self.open_temporary_download_location(code[1]))
            self.save_height = False

    def open_temporary_download_location(self, location):
        if sys.platform == 'win32':
            os.startfile(location)
        else:
            subprocess.call(['xdg-open', location])
        self.close()

    def closeEvent(self, QCloseEvent):
        if self.save_height:
            self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('launch_checkbox', self.launch_checkbox.isChecked())
        if self.launch_checkbox.isChecked() and self.launch_checkbox.isVisible():
            self.launch_program()
