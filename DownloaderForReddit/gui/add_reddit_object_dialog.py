import os
import logging
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.QtCore import Qt

from ..guiresources.add_reddit_object_dialog_auto import Ui_AddRedditObjectDialog
from ..utils import injector, system_util
from ..utils.importers import json_importer, text_importer


class AddRedditObjectDialog(QDialog, Ui_AddRedditObjectDialog):

    def __init__(self, list_model, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.list_model = list_model
        self.setWindowTitle(f'Add {self.list_model.list_type.capitalize()}')
        self.single_add_label.setText(f'Enter new {self.list_model.list_type.lower()}')
        self.tab_widget.setCurrentIndex(0)

        self.download_on_add_checkbox.setChecked(self.settings_manager.download_on_add)
        self.download_on_add_checkbox.stateChanged.connect(
            lambda checked: setattr(self.settings_manager, 'download_on_add', checked))

        self.add_button.clicked.connect(self.add_object_to_list)
        self.remove_button.clicked.connect(self.remove_object_from_list)
        self.import_button.clicked.connect(self.import_list)
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.close)

        self.single_object_line_edit.setFocus()
        self.tab_widget.currentChanged.connect(self.tab_change)

        self.added = []

    def tab_change(self):
        if self.tab_widget.currentIndex() == 0:
            self.single_object_line_edit.setFocus()
        else:
            self.multi_object_line_edit.setFocus()

    def refresh_name_count(self):
        self.name_count_label.setText(str(self.multi_object_list_widget.count()))

    def add_object_to_list(self):
        self.multi_object_list_widget.addItem(self.multi_object_line_edit.text())
        self.multi_object_line_edit.clear()
        self.refresh_name_count()

    def remove_object_from_list(self):
        for index in self.multi_object_list_widget.selectedIndexes():
            self.multi_object_list_widget.takeItem(index.row())
        self.refresh_name_count()

    def import_list(self):
        file_path = self.get_import_file_path()
        if file_path is not None:
            import_list = []
            if file_path.endswith('txt'):
                import_list = text_importer.import_list_from_text_file(file_path)
            elif file_path.endswith('json'):
                import_list = json_importer.import_list_from_json(file_path)
            self.multi_object_list_widget.addItems(import_list)

    def get_import_file_path(self):
        file_path = QFileDialog.getOpenFileName(self, 'Select Import File', system_util.get_data_directory(),
                                                'Import File (*.txt, *.json)')[0]
        if os.path.isfile(file_path):
            return file_path
        else:
            self.logger.error('Failed to import file.  File does not exist.', extra={'file_path': file_path})
            return None

    def accept(self):
        self.add_reddit_objects()
        super().accept()

    def add_reddit_objects(self):
        if self.tab_widget.currentIndex() == 0:
            name = self.single_object_line_edit.text()
            if name is not None and name != '':
                self.list_model.add_reddit_object(name)
        else:
            names = []
            for row in range(self.multi_object_list_widget.count()):
                name = self.multi_object_list_widget.item(row).text()
                if name is not None and name != '':
                    names.append(name)
            self.list_model.add_reddit_objects(names)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            if self.tab_widget.currentIndex() == 0:
                shift = QApplication.keyboardModifiers() == Qt.ShiftModifier
                if shift:
                    self.multi_object_list_widget.addItem(self.single_object_line_edit.text())
                    self.single_object_line_edit.clear()
                    self.tab_widget.setCurrentIndex(1)
                    self.refresh_name_count()
                else:
                    self.accept()
            else:
                self.add_object_to_list()
