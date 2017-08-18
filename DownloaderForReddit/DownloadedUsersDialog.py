import os
import re
import sys
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

from UserSettingsDialog import UserSettingsDialog


class DownloadedUsersDialog(UserSettingsDialog):

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
        super().__init__(list_model, clicked_user)
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

    def save_temporary_user(self):
        pass

    def download_single(self):
        pass

    def select_save_path_dialog(self):
        pass

    def change_page(self):
        pass

    def change_to_user_settings(self):
        pass

    def set_restore_defaults(self):
        pass

    def change_to_downloads_view(self):
        """Overwrites the parent classes method to remove renaming of buttons"""
        if self.page_two_geom is not None:
            self.resize(self.page_two_geom[0], self.page_two_geom[1])
        self.stacked_widget.setCurrentIndex(1)
        self.setup_user_content_list()

    def list_item_change(self):
        self.current_user = self.user_list[self.user_list_widget.currentRow()]
        self.setup_user_content_list()

    def toggle_download_views(self):
        """Toggles if images are shown"""
        if self.show_downloads:
            self.show_downloads = False
        else:
            self.show_downloads = True
        self.setup_user_content_list()

    def setup_user_content_list(self):
        """
        Overwrites the parent classes method so that only files that were downloaded during the last session and
        supplied via the last_downloaded_file_dict parameter are displayed
        """
        self.user_content_list.clear()
        if self.user_content_icons_full_width:
            icon_size = self.user_content_list.width()
        else:
            icon_size = self.user_content_icon_size
        self.user_content_list.setIconSize(QtCore.QSize(icon_size, icon_size))
        if self.show_downloads:
            try:
                if len(self.file_dict) > 0:
                    self.file_dict[self.current_user.name].sort(key=alphanum_key)
                    # for file in sorted(self.file_dict[self.current_user.name], key=alphanum_key):
                    for file in self.file_dict[self.current_user.name]:
                        file_name = file.rsplit('/', 1)[1]
                        item = QtWidgets.QListWidgetItem()
                        icon = QtGui.QIcon()
                        pixmap = QtGui.QPixmap(file).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)
                        icon.addPixmap(pixmap)
                        item.setIcon(icon)
                        item.setText(file_name)
                        self.user_content_list.addItem(item)
                        QtWidgets.QApplication.processEvents()

            except FileNotFoundError:
                self.user_content_list.addItem('No content has been downloaded for this user yet')

    def open_file(self, position):
        file = self.file_dict[self.current_user.name][position]
        try:
            if sys.platform == 'win32':
                os.startfile(file)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, file])
        except (AttributeError, FileNotFoundError):
            pass


# Functions that sort the displayed content in an expected manner
def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]
