import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QItemSelectionModel

from ..guiresources.reddit_object_settings_dialog_auto import Ui_RedditObjectSettingsDialog
from ..viewmodels.reddit_object_list_model import RedditObjectListModel
from ..utils import injector


class RedditObjectSettingsDialog(QtWidgets.QDialog, Ui_RedditObjectSettingsDialog):

    download_signal = pyqtSignal(list)

    def __init__(self, list_type, list_name, selected_object_ids: list, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.list_type = list_type
        self.list_name = list_name
        self.selected_objects = None

        geom = self.settings_manager.reddit_object_settings_dialog_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.splitter.setSizes(self.settings_manager.reddit_object_settings_dialog_splitter_state)

        self.dialog_button_box.accepted.connect(self.save_and_close)
        self.dialog_button_box.rejected.connect(self.close)
        self.reset_button.clicked.connect(self.reset)

        self.list_model = RedditObjectListModel(self.list_type)
        self.list_model.set_list(self.list_name)
        self.reddit_objects_list_view.setModel(self.list_model)

        id_list = self.list_model.get_id_list(download_enabled=False)
        indices = [id_list.index(x) for x in selected_object_ids]
        selected_objects = [self.list_model.reddit_objects[index] for index in indices]
        for row in indices:
            index = self.list_model.createIndex(row, 0)
            self.reddit_objects_list_view.selectionModel().select(index, QItemSelectionModel.Select)

        self.set_objects(selected_objects)
        self.reddit_objects_list_view.selectionModel().selectionChanged.connect(self.select_objects)

        self.download_button.clicked.connect(self.download)
        self.download_button.setToolTip(f'Save and download this {self.list_type.lower()}')

    def set_objects(self, object_list):
        self.selected_objects = object_list
        self.info_widget.set_objects(self.selected_objects)
        self.settings_widget.set_objects(self.selected_objects)
        if len(self.selected_objects) == 1:
            self.download_button.setText(f'Download {object_list[0].name}')
        else:
            self.download_button.setText(f'Download {len(self.selected_objects)} {self.list_type.lower()}s')

    def select_objects(self):
        indecies = self.reddit_objects_list_view.selectionModel().selectedRows(0)
        self.set_objects([self.list_model.raw_data(x.row()) for x in indecies])

    def save_and_close(self):
        self.list_model.session.commit()
        self.close()

    def reset(self):
        self.list_model.session.rollback()
        self.settings_widget.set_objects(self.selected_objects)

    def download(self):
        self.list_model.session.commit()
        self.download_signal.emit([x.id for x in self.selected_objects])

    def closeEvent(self, event):
        self.settings_manager.main_window_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
        self.settings_manager.reddit_object_settings_dialog_splitter_state = self.splitter.sizes()
        self.list_model.session.close()
