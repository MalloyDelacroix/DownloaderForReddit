import os
import logging
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from pyqtspinner.spinner import WaitingSpinner
from threading import Thread

from ..guiresources.add_reddit_object_dialog_auto import Ui_AddRedditObjectDialog
from ..utils import injector, system_util, reddit_utils
from ..utils.importers import json_importer, text_importer
from ..database.models import ListAssociation, RedditObject
from .existing_names_dialog import ExistingNamesDialog


class AddRedditObjectDialog(QDialog, Ui_AddRedditObjectDialog):

    validation_finished = pyqtSignal()

    def __init__(self, list_model, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
        self.list_model = list_model
        self.setWindowTitle(f'Add {self.list_model.list_type.capitalize()}')
        self.single_add_label.setText(f'Enter new {self.list_model.list_type.lower()}')
        self.tab_widget.setCurrentIndex(0)

        self.download_on_add_checkbox.setChecked(self.settings_manager.download_on_add)
        self.download_on_add_checkbox.stateChanged.connect(
            lambda checked: setattr(self.settings_manager, 'download_on_add', checked))

        self.validate_names_checkbox.setChecked(self.settings_manager.validate_names_before_add)
        self.validate_names_checkbox.stateChanged.connect(
            lambda checked: setattr(self.settings_manager, 'validate_names_before_add', checked)
        )

        self.add_button.clicked.connect(self.add_object_to_list)
        self.remove_button.clicked.connect(self.remove_object_from_list)
        self.import_button.clicked.connect(self.import_list)
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.close)

        self.single_object_line_edit.setFocus()
        self.tab_widget.currentChanged.connect(self.tab_change)

        self.added = []
        self.imported = []
        self.exclude = []

    def tab_change(self):
        if self.tab_widget.currentIndex() == 0:
            self.single_object_line_edit.setFocus()
        else:
            self.multi_object_line_edit.setFocus()

    def refresh_name_count(self):
        self.name_count_label.setText(str(self.multi_object_list_widget.count()))

    def add_object_to_list(self):
        text = self.multi_object_line_edit.text().strip()
        names = text.replace('\n', ',').split(',')
        for name in names:
            name = name.strip()
            if name != '' and name not in self.added:
                self.added.append(name)
                self.multi_object_list_widget.addItem(name)
                self.multi_object_line_edit.clear()
                self.refresh_name_count()

    def remove_object_from_list(self):
        for index in self.multi_object_list_widget.selectedIndexes():
            self.multi_object_list_widget.takeItem(index.row())
        self.refresh_name_count()

    def import_list(self):
        file_path = self.get_import_file_path()
        if file_path is not None and os.stat(file_path).st_size > 0:
            if file_path.endswith('txt'):
                import_list = text_importer.import_list_from_text_file(file_path)
                self.added.extend(import_list)
                self.multi_object_list_widget.addItems(import_list)
                self.refresh_name_count()
            elif file_path.endswith('json'):
                imported_objects = json_importer.import_json(file_path)
                self.validate_imported_objects(imported_objects)
                self.refresh_name_count()

    def get_import_file_path(self):
        file_path = QFileDialog.getOpenFileName(self, 'Select Import File', system_util.get_data_directory(),
                                                'Text Files (*.txt *.json)')[0]
        if file_path is not None and file_path != '':
            if os.path.isfile(file_path):
                return file_path
            else:
                self.logger.error('Failed to import file.  File does not exist.', extra={'file_path': file_path})
                return None

    def validate_imported_objects(self, imported_objects):
        self.spinner = WaitingSpinner(parent=None, roundness=80.0, opacity=10.0, fade=72.0, radius=10.0,
                                 lines=12, line_length=12.0, line_width=4.0, speed=1.4, color=(0, 0, 0))
        self.spinner.setParent(self.multi_object_list_widget)
        self.validation_finished.connect(self.spinner.stop)  # signal used to stop timer in correct thread
        self.spinner.start()
        self.thread = Thread(target=self.validate_objects, args=imported_objects)
        self.thread.start()

    def validate_objects(self, *imported_objects):
        name_checker = reddit_utils.NameChecker(self.list_model.list_type)
        for ro in imported_objects:
            v_set = name_checker.check_reddit_object_name(ro.name)
            if v_set.valid:
                ro.name = v_set.name
                ro.date_created = v_set.date_created
                self.imported.append(ro)
                self.multi_object_list_widget.addItem(ro.name)
        self.validation_finished.emit()

    def accept(self):
        self.add_reddit_objects()
        super().accept()

    def add_reddit_objects(self):
        if self.settings_manager.check_existing_reddit_objects:
            self.filter_existing()
        if self.tab_widget.currentIndex() == 0:
            name = self.single_object_line_edit.text().strip()
            if name is not None and name != '' and name not in self.exclude:
                self.list_model.add_reddit_object(name)
        else:
            add = [x for x in self.added if x not in self.exclude]
            self.list_model.add_reddit_objects(add)
        self.add_imported_reddit_objects()

    def filter_existing(self):
        with self.db.get_scoped_session() as session:
            if self.tab_widget.currentIndex() == 0:
                check = [self.single_object_line_edit.text().strip()]
            else:
                check = self.added
            existing_names = {}
            for name in check:
                lists = self.check_existing(name, session)
                if len(lists) > 0:
                    existing_names[name] = lists
            for ro in self.imported:
                lists = self.check_existing(ro.name, session)
                if len(lists) > 0:
                    existing_names[ro.name] = lists
            if len(existing_names) > 0:
                dialog = ExistingNamesDialog(existing_names)
                dialog.exec_()
                for key, value in dialog.decisions.items():
                    if not value:
                        self.exclude.append(key)

    def check_existing(self, name, session):
        ro_list = session.query(ListAssociation).join(RedditObject).filter(RedditObject.name == name)
        return [x.reddit_object_list.name for x in ro_list]

    def add_imported_reddit_objects(self):
        for ro in self.imported:
            if ro.name not in self.exclude:
                self.list_model.add_complete_reddit_object(ro)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            if self.tab_widget.currentIndex() == 0:
                shift = QApplication.keyboardModifiers() == Qt.ShiftModifier
                if shift:
                    name = self.single_object_line_edit.text().strip()
                    if name != '' and name not in self.added:
                        self.added.append(name)
                        self.multi_object_list_widget.addItem(name)
                        self.single_object_line_edit.clear()
                        self.tab_widget.setCurrentIndex(1)
                        self.refresh_name_count()
                else:
                    self.accept()
            else:
                self.add_object_to_list()
