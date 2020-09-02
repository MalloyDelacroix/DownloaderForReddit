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


from PyQt5.QtWidgets import QDialog

from ..guiresources.update_dialog_auto import Ui_update_dialog_box
from ..utils import injector
from ..version import __version__


class UpdateDialog(QDialog, Ui_update_dialog_box):

    def __init__(self, update_variables, parent=None):
        """
        Class that displays update information if it is available with a link to the github release page to download
        the new version of the application

        :param update_variables: The new version number

        Right now the update_variables are really only the new version number of the app that is available.  In the
        future this will hopefully be expanded
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        self.parent = parent
        self.settings_manager = injector.settings_manager

        self.new_version = update_variables
        self.old_version = __version__
        self.new_version = update_variables
        self.label.setWordWrap(True)
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setWordWrap(True)
        self.label.setText("A new version of The Downloader for Reddit is available.\n\nCurrent Version: %s\nNew "
                           "Version: %s" %
                           (self.old_version,  self.new_version))
        self.link_label.setText('Please follow this link to download the new version: '
                                '<a href="https://github.com/MalloyDelacroix/DownloaderForReddit/releases">Downloader '
                                'for Reddit - Version %s '
                                '</a>' % self.new_version)
        self.link_label.setToolTip("https://github.com/MalloyDelacroix/DownloaderForReddit/releases")

        self.direct_link_label.setVisible(False)

        self.buttonBox.accepted.connect(self.close_dialog)

        self.go_to_settings_label.clicked.connect(
            lambda: self.parent.open_settings_dialog(open_display='Notifications'))

    def close_dialog(self):
        self.close()

    def closeEvent(self, QCloseEvent):
        if self.do_not_notify_checkbox.isChecked():
            self.settings_manager.ignore_update = self.new_version
            self.settings_manager.update_dialog_geom = self.saveGeometry()
