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


from PyQt5 import QtWidgets, QtCore, QtGui

from GUI.RedditObjectSettingsDialog import RedditObjectSettingsDialog
from Core import SystemUtil
from Core.AlphanumKey import ALPHANUM_KEY


class DownloadedUsersDialog(RedditObjectSettingsDialog):

    def __init__(self, list_model, clicked_user, last_downloaded_file_dict):
        """
        Class that displays downloaded user content that was downloaded during the current running session.  This
        dialog is the UserSettingsDialog with many features stripped out, and some methods overwritten to provide only
        thumbnails of the last downloaded images.

        :param list_model: A list of user objects that had content downloaded during the session
        :param clicked_user: The first user in the list
        :param last_downloaded_file_dict: A dictionary with the key being the downloaded user and the value being a list
        of files downloaded during the session
        """
        super().__init__(list_model, clicked_user, False)
        self.file_dict = last_downloaded_file_dict
        self.view_downloads_button.clicked.connect(self.toggle_download_views)
        self.view_downloads_button.setText('Show Downloads')
        self.restore_defaults_button.setVisible(False)
        self.restore_defaults_button.setEnabled(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')

    """
    The following methods are overwritten from the UserSettingsDialog to prevent any changes to user objects
    as well as to limit non wanted functionality when using this dialog
    """
    def setup(self):
        pass

    def setup_display(self, reddit_object):
        pass

    def set_save_path_name_label(self):
        pass

    def get_name_label_text(self):
        pass

    def save_temp_object(self):
        pass

    def download_single(self):
        pass

    def select_save_path_dialog(self):
        pass

    def change_page(self):
        pass

    def change_to_settings_view(self):
        pass

    def set_restore_defaults(self):
        pass

    def change_to_downloads_view(self):
        """Overwrites the parent classes method to remove renaming of buttons"""
        if self.page_two_geom is not None:
            self.resize(self.page_two_geom[0], self.page_two_geom[1])
        self.stacked_widget.setCurrentIndex(1)
        self.setup_content_list()

    def list_item_change(self):
        self.current_object = self.object_list[self.object_list_widget.currentRow()]
        self.setup_content_list()

    def toggle_download_views(self):
        """Toggles if images are shown"""
        if self.show_downloads:
            self.show_downloads = False
        else:
            self.show_downloads = True
        self.setup_content_list()

    def setup_content_list(self):
        """
        Overwrites the parent classes method so that only files that were downloaded during the last session and
        supplied via the last_downloaded_file_dict parameter are displayed
        """
        self.content_list.clear()
        if self.content_icons_full_width:
            icon_size = self.content_list.width()
        else:
            icon_size = self.content_icon_size
        self.content_list.setIconSize(QtCore.QSize(icon_size, icon_size))
        if self.show_downloads:
            try:
                if len(self.file_dict) > 0:
                    self.file_dict[self.current_object.name].sort(key=ALPHANUM_KEY)
                    for file in self.file_dict[self.current_object.name]:
                        file_name = file.rsplit('/', 1)[1]
                        item = QtWidgets.QListWidgetItem()
                        icon = QtGui.QIcon()
                        pixmap = QtGui.QPixmap(file).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)
                        icon.addPixmap(pixmap)
                        item.setIcon(icon)
                        item.setText(file_name)
                        self.content_list.addItem(item)
                        QtWidgets.QApplication.processEvents()

            except FileNotFoundError:
                self.content_list.addItem('No content has been downloaded for this user yet')

    def open_file(self):
        file = self.file_dict[self.current_object.name][self.content_list.currentIndex().row()]
        SystemUtil.open_in_system(file)
