from PyQt5 import QtWidgets, QtCore

from DFR_Updater.UpdaterGUI_auto import Ui_updater_gui
from DFR_Updater.Updater import Updater


class UpdaterWidget(QtWidgets.QWidget, Ui_updater_gui):

    cancel_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.settings = QtCore.QSettings('SomeGuySoftware', 'dfr_updater')
        self.download_url = self.settings.value('download_url', None, type=str)
        self.download_name = self.settings.value('download_name', None, type=str)
        self.new_version = self.settings.value('new_version', None, type=str)
        # self.program_files_location = self.settings.value('program_files_location', None, type=str)

    def run(self):
        self.thread = QtCore.QThread()
        self.updater = Updater(self.download_url, self.download_name, self.new_version, None)
        self.cancel_signal.connect(self.updater.stop)
        self.updater.moveToThread(self.thread)
        self.thread.started.connect(self.updater.run)
        self.updater.set_label.connect(self.update_label)
        self.updater.setup_progress_bar.connect(self.setup_progress_bar)
        self.updater.update_progress_bar.connect(self.update_progress_bar)
        self.updater.finished.connect(self.thread.quit)
        self.updater.finished.connect(self.updater.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def update_label(self, text):
        pass

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








