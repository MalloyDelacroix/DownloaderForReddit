from PyQt5.QtWidgets import QWidget
import logging

from DownloaderForReddit.utils import injector


class AbstractSettingsWidget(QWidget):

    def __init__(self, init_ui=True):
        QWidget.__init__(self)
        if init_ui:
            self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings = injector.get_settings_manager()
        self.loaded = False

    @property
    def description(self):
        return None

    def load(self):
        self.load_settings()
        self.loaded = True

    def load_settings(self):
        pass

    def apply(self):
        if self.loaded:
            self.apply_settings()

    def apply_settings(self):
        pass
