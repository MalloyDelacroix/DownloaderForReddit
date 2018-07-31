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


from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QCursor

from GUI_Resources.AddRedditObjectDialog_auto import Ui_add_reddit_object_dialog
from ViewModels.AddRedditObjectListModel import AddRedditObjectListModel
import Utils.Injector


class AddUserDialog(QtWidgets.QDialog, Ui_add_reddit_object_dialog):

    def __init__(self, object_type):
        """
        A dialog that opens to allow for the user to add a new reddit username to the username list. An instance of this
        class is also used as a dialog to add subreddits, but two object names are overwritten. This dialog is basically
        a standard input dialog, but with the addition of a third button that allows the user to add more than one name
        without closing the dialog.  Shortcut keys have also been added to facilitate ease of use
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.settings_manager = Utils.Injector.get_settings_manager()
        self.object_type = object_type
        geom = self.settings_manager.add_user_dialog_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())

        self.object_name_list_view = QtWidgets.QListView()
        self.object_name_list_model = AddRedditObjectListModel()
        self.object_name_list_view.setModel(self.object_name_list_model)
        self.add_to_list_button = QtWidgets.QToolButton()
        self.add_to_list_button.setText('+')
        self.remove_from_list_button = QtWidgets.QToolButton()
        self.remove_from_list_button.setText('-')
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.add_to_list_button)
        self.button_layout.addWidget(self.remove_from_list_button)
        self.list_layout = QtWidgets.QVBoxLayout()
        self.list_layout.addWidget(self.object_name_list_view)
        self.list_layout.addLayout(self.button_layout)

        self.name = None
        self.name_list = []

        self.ok_cancel_button_box.accepted.connect(self.accept)
        self.ok_cancel_button_box.rejected.connect(self.close)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self):
        menu = QtWidgets.QMenu()
        toggle_text = 'Switch To List' if self.vert_layout.indexOf(self.object_name_line_edit) >= 0 else \
            'Switch To Single Line'
        toggle_layout = menu.addAction(toggle_text)
        import_from_file = menu.addAction('Import From File')
        import_from_directory = menu.addAction('Import From Directory')

        toggle_layout.triggered.connect(self.toggle_layout)
        import_from_file.triggered.connect(self.import_from_file)
        import_from_directory.triggered.connect(self.import_from_directory)
        menu.exec(QCursor.pos())

    def toggle_layout(self):
        if self.vert_layout.indexOf(self.object_name_line_edit) >= 0:
            self.setup_list_view()
        else:
            self.setup_line_edit_view()

    def setup_list_view(self):
        if self.object_name_line_edit.text() != '' and self.object_name_line_edit.text() is not None:
            self.object_name_list_model.insertRow(self.object_name_line_edit.text())
        index = self.vert_layout.indexOf(self.object_name_line_edit)
        self.vert_layout.removeWidget(self.object_name_line_edit)
        self.object_name_line_edit.close()
        self.vert_layout.insertLayout(index, self.list_layout)
        self.vert_layout.update()

    def setup_line_edit_view(self):
        pass

    def keyPressEvent(self, event):
        key = event.key()
        mod = QtWidgets.QApplication.keyboardModifiers()
        if key == QtCore.Qt.Key_Return and mod == QtCore.Qt.ShiftModifier:
            self.add_another_button.click()
        if key == QtCore.Qt.Key_Enter and mod == QtCore.Qt.ShiftModifier:
            self.add_another_button.click()
        if key == QtCore.Qt.Key_Return and not mod == QtCore.Qt.ShiftModifier:
            self.accept()
        if key == QtCore.Qt.Key_Enter and not mod == QtCore.Qt.ShiftModifier:
            self.accept()

    def import_from_file(self):
        pass

    def import_from_directory(self):
        pass

    # def add_multiple(self):
    #     self.name = self.user_name_line_edit.text()
    #     self.user_name_line_edit.clear()
    #     self.user_name_line_edit.setFocus()

    def accept(self):
        self.name = self.user_name_line_edit.text()
        self.save_settings()
        super().accept()

    def closeEvent(self, QCloseEvent):
        self.save_settings()

    def save_settings(self):
        self.settings_manager.add_user_dialog_geom = self.saveGeometry()
        self.settings_manager.save_add_user_dialog()
