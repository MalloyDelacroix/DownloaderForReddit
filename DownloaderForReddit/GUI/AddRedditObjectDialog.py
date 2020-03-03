"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QCursor
import logging

from ..GUI_Resources.AddRedditObjectDialog_auto import Ui_add_reddit_object_dialog
from ..ViewModels.AddRedditObjectListModel import AddRedditObjectListModel
from ..Utils import Injector
from ..Utils.Importers import TextImporter, JsonImporter, XMLImporter
from DownloaderForReddit.GUI.Messages import Message


class AddUserDialog(QtWidgets.QDialog, Ui_add_reddit_object_dialog):

    def __init__(self, object_type, parent=None):
        """
        A dialog that opens to allow for the user to add a new reddit username to the username list. An instance of this
        class is also used as a dialog to add subreddits, but two object names are overwritten. This dialog is basically
        a standard input dialog, but with the addition of a third button that allows the user to add more than one name
        without closing the dialog.  Shortcut keys have also been added to facilitate ease of use
        """
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.settings_manager = Injector.get_settings_manager()
        self.object_type = object_type
        self.layout_style = 'SINGLE'

        self.object_name_list_view = QtWidgets.QListView()
        self.object_name_list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_name_list_model = AddRedditObjectListModel(self.object_type, self)
        self.object_name_list_model.name_list_updated.connect(self.name_count_updated)
        self.object_name_list_view.setModel(self.object_name_list_model)

        self.name_count_label = QtWidgets.QLabel()
        self.add_to_list_button = QtWidgets.QToolButton()
        self.add_to_list_button.setText('+')
        self.add_to_list_button.clicked.connect(self.add_name_to_list)
        self.remove_from_list_button = QtWidgets.QToolButton()
        self.remove_from_list_button.setText('-')
        self.remove_from_list_button.clicked.connect(self.remove_name_from_list)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.name_count_label)
        self.button_layout.addWidget(self.add_to_list_button)
        self.button_layout.addWidget(self.remove_from_list_button)
        self.list_layout = QtWidgets.QVBoxLayout()
        self.list_layout.addWidget(self.object_name_list_view)
        self.list_layout.addLayout(self.button_layout)

        self.name = None

        self.init_download_on_add_checkbox()
        self.download_on_add_checkbox.toggled.connect(self.toggle_download_on_add_checkbox)

        self.ok_cancel_button_box.accepted.connect(self.accept)
        self.ok_cancel_button_box.rejected.connect(self.close)

        self.object_name_line_edit.textChanged.connect(self.check_line_edit_text)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.show_context_menu(False))

        self.object_name_line_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.object_name_line_edit.customContextMenuRequested.connect(lambda: self.show_context_menu(True))

    def show_context_menu(self, text_edit):
        """
        Creates a context menu for the dialog with options to switch the ui between the single line input and the list
        input, as well as options for importing a list of reddit objects.
        :param text_edit: True if the context menu is being requested from a line edit.  If True, standard copy and
                          paste methods will be included in the context menu.
        """
        menu = QtWidgets.QMenu()
        if text_edit:
            copy = menu.addAction('Copy')
            paste = menu.addAction('Paste')
            menu.addSeparator()
            copy.triggered.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.object_name_line_edit.text()))
            paste.triggered.connect(lambda:
                                    self.object_name_line_edit.setText(QtWidgets.QApplication.clipboard().text()))
        toggle_text = 'Switch To List' if self.layout_style == 'SINGLE' else 'Switch To Single Line'
        toggle_layout = menu.addAction(toggle_text)
        import_text_file = menu.addAction('Import From Text File')
        import_json_file = menu.addAction('Import From Json File')
        import_xml_file = menu.addAction('Import From Xml File')
        import_from_directory = menu.addAction('Import From Directory')

        if self.layout_style == 'MULTIPLE':
            menu.addSeparator()
            clear_non_valid = menu.addAction('Clear All Non Valid')
            clear_non_valid.triggered.connect(self.object_name_list_model.clear_non_valid)

        toggle_layout.triggered.connect(self.toggle_layout)
        import_text_file.triggered.connect(self.import_from_text_file)
        import_json_file.triggered.connect(self.import_from_json_file)
        import_xml_file.triggered.connect(self.import_from_xml_file)
        import_from_directory.triggered.connect(self.import_from_directory)

        menu.exec(QCursor.pos())

    def toggle_layout(self):
        if self.layout_style == 'SINGLE':
            self.setup_list_view()
        else:
            self.setup_line_edit_view()

    def setup_list_view(self):
        self.vert_layout.insertLayout(0, self.list_layout)
        self.add_name_to_list()
        self.download_on_add_checkbox.setVisible(False)
        self.layout_style = 'MULTIPLE'

    def setup_line_edit_view(self):
        self.vert_layout.removeItem(self.list_layout)
        self.download_on_add_checkbox.setVisible(True)
        self.layout_style = 'SINGLE'

    def name_count_updated(self):
        self.object_name_list_view.scrollToBottom()
        self.name_count_label.setText('%s names in list' % len(self.object_name_list_model.name_list))

    def init_download_on_add_checkbox(self):
        if self.object_type == 'USER':
            checked = self.settings_manager.download_users_on_add
        else:
            checked = self.settings_manager.download_subreddits_on_add
        self.download_on_add_checkbox.setChecked(checked)
        self.download_on_add_checkbox.setToolTip(
            'Added {reddit_object} will be downloaded immediately after being added.\n'
            'Not available when download is in progress or in multi-add mode'.format(
                reddit_object=self.object_type.lower())
        )

    def toggle_download_on_add_checkbox(self):
        """
        Handles changing the settings in the settings manager that dictates if users or subreddits are downloaded
        automatically after being added.  Will handle differently depending on if this dialog is being used for adding
        users or subreddits.  This setting is saved to the system on toggle, not on dialog accept or close.
        """
        if self.object_type == 'USER':
            self.settings_manager.download_users_on_add = self.download_on_add_checkbox.isChecked()
        else:
            self.settings_manager.download_subreddits_on_add = self.download_on_add_checkbox.isChecked()
        self.settings_manager.save_add_dialog()

    def keyPressEvent(self, event):
        key = event.key()
        mod = QtWidgets.QApplication.keyboardModifiers()
        if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and mod == QtCore.Qt.ShiftModifier:
            self.alt_return_action()
        elif key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.return_action()
        if key == QtCore.Qt.Key_Delete:
            if self.layout_style == 'MULTIPLE':
                self.object_name_list_model.removeRows(self.object_name_list_view.currentIndex().row(),
                                                       len(self.object_name_list_view.selectedIndexes()))

    def return_action(self):
        """Handles a keyboard event equal to return or enter depending on the current layout style."""
        if self.layout_style == 'SINGLE':
            self.accept()
        else:
            self.add_name_to_list()

    def alt_return_action(self):
        """
        Handles a keyboard event equal to return or enter if the shift modifier key is also pressed depending on the
        layout style.
        """
        if self.layout_style == 'SINGLE':
            self.toggle_layout()
        else:
            self.add_name_to_list()

    def import_from_text_file(self):
        file_path = self.select_file(('Select Text File', 'Text File (*.txt)'))
        count = 0
        if file_path is not None and file_path.endswith('txt'):
            for name in TextImporter.import_list_from_text_file(file_path):
                self.add_name_to_list(name)
                count += 1
        self.setup_list_view()
        self.logger.info('Imported %s reddit object names from text file' % count)

    def import_from_json_file(self):
        file_path = self.select_file(('Select Json File', 'Json File (*.json)'))
        count = 0
        if file_path is not None and file_path.endswith('json'):
            for ro in JsonImporter.import_list_from_json(file_path):
                self.add_complete_object_to_list(ro)
                count += 1
        self.setup_list_view()
        self.logger.info('Imported %s complete reddit objects from json file' % count)

    def import_from_xml_file(self):
        file_path = self.select_file(('Select Xml File', 'Xml File (*.xml)'))
        count = 0
        if file_path is not None and file_path.endswith('xml'):
            for ro in XMLImporter.import_list_from_xml(file_path):
                self.add_complete_object_to_list(ro)
        self.setup_list_view()
        self.logger.info('Imported %s complete reddit objects from xml file' % count)

    def select_file(self, var):
        """
        Opens a dialog for the user to select a text file and returns the path to the selected file if it exists.
        :return: The path to the user selected file.
        :rtype: str
        """
        file_path = str(QtWidgets.QFileDialog.getOpenFileName(self, var[0], self.settings_manager.save_directory,
                                                              var[1])[0])
        if os.path.isfile(file_path):
            return file_path
        else:
            self.logger.warning('Tried to import invalid file: %s' % file_path)
            Message.invalid_file_path(self)
            return None

    def import_from_directory(self):
        """
        Imports a list of names form a directory.  Each subfolder in the directory will be registered as a name to be
        added.
        """
        master_folder = self.select_directory()
        if master_folder is not None:
            reply = QtWidgets.QMessageBox.information(self, 'Import From Folder?',
                                                      'Import names of all subfolders from %s?' % master_folder,
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Ok:
                count = 0
                for folder in (folder for folder in os.listdir(master_folder) if
                               os.path.isdir(os.path.join(master_folder, folder))):
                    self.add_name_to_list(name=folder)
                    count += 1
                if self.layout_style == 'SINGLE':
                    self.toggle_layout()
                self.logger.info('Imported %s reddit object names from folders' % count)

    def select_directory(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select The Folder to Import From',
                                                                self.settings_manager.save_directory))
        if os.path.isdir(folder):
            return folder
        else:
            Message.invalid_file_path(self)
            return None

    def check_line_edit_text(self):
        if '\n' in self.object_name_line_edit.text() or ',' in self.object_name_line_edit.text():
            if self.layout_style == 'SINGLE':
                self.toggle_layout()
            else:
                self.object_name_line_edit.setText(self.object_name_line_edit.text().replace(',', '').replace('\n', ''))
                self.add_name_to_list()

    def add_name_to_list(self, name=None):
        if not name:
            name = self.object_name_line_edit.text().replace('\n', ',').lstrip().strip()
        if name is not None and name != '':
            name_list = name.split(',')
            for name in name_list:
                if name is not None and name != '' and ' ' not in name:
                    self.object_name_list_model.insertRow(name)
        self.object_name_line_edit.clear()

    def add_complete_object_to_list(self, ro):
        if ro is not None:
            self.object_name_list_model.add_complete_object(ro)

    def remove_name_from_list(self):
        self.object_name_list_model.removeRows(self.object_name_list_view.currentIndex().row(),
                                               len(self.object_name_list_view.selectedIndexes()))

    def accept(self):
        self.object_name_list_model.stop_name_checker()
        if self.layout_style == 'SINGLE':
            self.name = self.object_name_line_edit.text()
        else:
            for ro in self.object_name_list_model.complete_reddit_object_list:
                if ro.name in self.object_name_list_model.name_list:
                    self.object_name_list_model.name_list.remove(ro.name)
        super().accept()

    def closeEvent(self, event):
        self.object_name_list_model.stop_name_checker()
