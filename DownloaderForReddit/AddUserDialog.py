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

from AddUserDialog_auto import Ui_add_user_dialog


class AddUserDialog(QtWidgets.QDialog, Ui_add_user_dialog):

    def __init__(self):
        """
        A dialog that opens to allow for the user to add a new reddit username to the username list. An instance of this
        class is also used as a dialog to add subreddits, but two object names are overwritten. This dialog is basically
        a standard input dialog, but with the addition of a third button that allows the user to add more than one name
        without closing the dialog.  Shortcut keys have also been added to facilitate ease of use
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.name = None

        self.ok_cancel_button_box.accepted.connect(self.accept)
        self.ok_cancel_button_box.rejected.connect(self.close)
        self.add_another_button.clicked.connect(self.add_multiple)

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

    def add_multiple(self):
        self.name = self.user_name_line_edit.text()
        self.user_name_line_edit.clear()
        self.user_name_line_edit.setFocus()

    def accept(self):
        self.name = self.user_name_line_edit.text()
        super().accept()
