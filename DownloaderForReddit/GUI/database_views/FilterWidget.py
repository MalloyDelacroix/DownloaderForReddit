from PyQt5.QtWidgets import QWidget

from DownloaderForReddit.GUI_Resources.database_views.FilterWidget_auto import Ui_FilterWidget


class FilterWidget(QWidget, Ui_FilterWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

    def filter(self, model):
        return []
