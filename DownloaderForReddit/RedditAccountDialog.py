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

from RedditAccoundDialog_auto import Ui_reddit_account_dialog


class RedditAccountDialog(QtWidgets.QDialog, Ui_reddit_account_dialog):
    """
    This class is not currently used.  It will eventually (hopefully) allow users to link the application to their
    reddit account for extra features, so I'm keeping it around as a reminder
    """
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.settings = QtCore.QSettings('ApexSoftware', 'RedditDownloader')

        self.reddit_account_help_button.clicked.connect(self.help_dialog)
        self.save_cancel_button_box.accepted.connect(self.accept)
        self.save_cancel_button_box.rejected.connect(self.close)

        self.username_line_edit.setText(self.settings.value('username_line_edit', '', type=str))
        self.password_line_edit.setText(self.settings.value('password_line_edit', '', type=str))

    def help_dialog(self):
        pass

    def accept(self):
        self.settings.setValue('username_line_edit', self.username_line_edit.text())
        self.settings.setValue('password_line_edit', self.password_line_edit.text())
        super().accept()
