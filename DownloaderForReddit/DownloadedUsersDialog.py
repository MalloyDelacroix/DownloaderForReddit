import os
import re
from PyQt5 import QtWidgets, QtCore, QtGui

from UserSettingsDialog import UserSettingsDialog


class DownloadedUsersDialog(UserSettingsDialog):

    def __init__(self, list_model, clicked_user, last_downloads):
        super().__init__(list_model, clicked_user)
        self.last_downloads = last_downloads
        self.view_downloads_button.clicked.connect(self.toggle_download_views)
        self.view_downloads_button.setText('Show Downloads')
        self.restore_defaults_button.setVisible(False)
        self.restore_defaults_button.setEnabled(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')

    def toggle_download_views(self):
        if self.show_downloads:
            self.show_downloads = False
        else:
            self.show_downloads = True
        self.setup_user_content_list()

    def setup_user_content_list(self):
        self.user_content_list.clear()
        if self.user_content_icons_full_width:
            icon_size = self.user_content_list.width()
        else:
            icon_size = self.user_content_icon_size
        self.user_content_list.setIconSize(QtCore.QSize(icon_size, icon_size))
        if self.show_downloads:
            try:
                self.user_folder = sorted([x for x in os.listdir(self.current_user.save_path)
                                           if os.path.isfile(os.path.join(self.current_user.save_path, x)) and
                                           x.lower().endswith(('.jpg', '.jpeg', '.png')) and x in self.last_downloads],
                                          key=alphanum_key)
                if len(self.user_folder) > 0:
                    for file in self.user_folder:
                        file_path = '%s%s%s' % (self.current_user.save_path, '/' if not
                        self.current_user.save_path.endswith('/') else '', file)
                        item = QtWidgets.QListWidgetItem()
                        icon = QtGui.QIcon()
                        pixmap = QtGui.QPixmap(file_path).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)
                        icon.addPixmap(pixmap)
                        item.setIcon(icon)
                        item.setText(str(file))
                        self.user_content_list.addItem(item)
                        QtWidgets.QApplication.processEvents()

            except FileNotFoundError:
                self.user_content_list.addItem('No content has been downloaded for this user yet')


# Functions that sort the displayed content in an expected manner
def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]
