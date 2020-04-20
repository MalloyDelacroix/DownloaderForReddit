import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from ..GUI_Resources.RedditObjectSettingsDialog_auto import Ui_RedditObjectSettingsDialog
from ..ViewModels.RedditObjectListModel import RedditObjectListModel
from ..Utils import Injector


class RedditObjectSettingsDialog(QtWidgets.QDialog, Ui_RedditObjectSettingsDialog):

    download_signal = pyqtSignal(int)

    def __init__(self, list_type, list_name, selected_object_id: int):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.list_type = list_type
        self.list_name = list_name
        self.selected_object = None

        geom = self.settings_manager.reddit_object_settings_dialog_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.splitter.setSizes(self.settings_manager.reddit_object_settings_dialog_splitter_state)

        self.dialog_button_box.accepted.connect(self.save_and_close)
        self.dialog_button_box.rejected.connect(self.close)
        self.reset_button.clicked.connect(self.reset)

        self.reddit_objects_list_view.clicked.connect(
            lambda x: self.set_objects(self.list_model.data(x, 'RAW_DATA'))
        )
        self.list_model = RedditObjectListModel(self.list_type)
        self.list_model.set_list(self.list_name)
        self.reddit_objects_list_view.setModel(self.list_model)
        index = self.list_model.index(self.list_model.get_id_list().index(selected_object_id), 0)
        self.set_objects(self.list_model.data(index, 'RAW_DATA'))
        self.reddit_objects_list_view.setCurrentIndex(index)

        self.download_button.clicked.connect(self.download)
        self.download_button.setToolTip(f'Save and download this {self.list_type.lower()}')

    def set_objects(self, new_object):
        self.selected_object = new_object
        self.info_widget.set_object(self.selected_object)
        self.settings_widget.set_object(self.selected_object)
        self.download_button.setText(f'Download {new_object.name}')

    def save_and_close(self):
        self.list_model.session.commit()
        self.close()

    def reset(self):
        self.list_model.session.rollback()
        self.settings_widget.set_object(self.selected_object)

    def download(self):
        self.list_model.session.commit()
        self.download_signal.emit(self.selected_object.id)

    def closeEvent(self, event):
        self.settings_manager.main_window_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
        self.settings_manager.reddit_object_settings_dialog_splitter_state = self.splitter.sizes()
