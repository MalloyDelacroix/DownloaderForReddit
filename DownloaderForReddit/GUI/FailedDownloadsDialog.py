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


from PyQt5 import QtWidgets

from GUI_Resources.FailedDownloadsDialog_auto import Ui_failed_downloads_dialog
import Utils.Injector


class FailedDownloadsDialog(QtWidgets.QDialog, Ui_failed_downloads_dialog):

    def __init__(self, fail_list):
        """
        A dialog box that shows the failed downloads and any relevent information about them, such as: the user that
        posted the content to reddit, the subreddit it was posted in, the title of the post, the url that failed and
        a reason as to why it failed (ex: download or extraction error)

        :param fail_list: A list supplied to the dialog of the failed content
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.settings_manager = Utils.Injector.get_settings_manager()
        geom = self.settings_manager.failed_downloads_dialog_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())

        for x in fail_list:
            self.textBrowser.append(x)
            self.textBrowser.append(' ')

        self.buttonBox.accepted.connect(self.accept)

    def accept(self):
        self.save_settings()
        super().accept()

    def closeEvent(self, event):
        self.save_settings()

    def save_settings(self):
        self.settings_manager.failed_downloads_dialog_geom = self.saveGeometry()
        self.settings_manager.save_failed_downloads_dialog()
