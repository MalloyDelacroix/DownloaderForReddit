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
import sys
import shutil
import datetime
import time
from PyQt5 import QtWidgets, QtCore
from ImgurClientDialog import ImgurClientDialog
from Messages import Message
if sys.platform == 'win32':
    from RD_settings_auto import Ui_Settings
elif sys.platform == 'darwin':
    from SettingsGUI_mac_auto import Ui_Settings
else:
    from SettingsGUI_linux_auto import Ui_Settings



class RedditDownloaderSettingsGUI(QtWidgets.QDialog, Ui_Settings):

    def __init__(self):
        """
        A dialog class where various options in the application are set
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self._restore_defaults = False

        self.settings = QtCore.QSettings("SomeGuySoftware", "RedditDownloader")

        self.reddit_account_link_button.setVisible(False)
        self.reddit_account_link_button.setEnabled(False)

        self.save_cancel_button_box.accepted.connect(self.accept)
        self.save_cancel_button_box.rejected.connect(self.close)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.imgur_client_button.clicked.connect(self.set_imgur_client)
        self.backup_select_folder_button.clicked.connect(self.backup_save_file)
        self.backup_import_file_button.clicked.connect(self.import_backup_file)

        self.restrict_to_score_checkbox.stateChanged.connect(self.restrict_score_shift)
        self.sub_sort_top_radio.toggled.connect(self.sub_sort_top_change)

        self.save_directory_dialog_button.clicked.connect(self.select_save_path)

        self.imgur_client_id = self.settings.value('imgur_client_id', None, type=str)
        self.imgur_client_secret = self.settings.value('imgur_client_secret', None, type=str)
        self.reddit_account_username = self.settings.value('reddit_account_username', None, type=str)
        self.reddit_account_password = self.settings.value('reddit_account_password', None, type=str)
        self.auto_save_checkbox.setCheckState(self.settings.value('auto_save_checkbox', 0, type=int))
        self.date_restriction_checkbox.setCheckState(self.settings.value('date_restriction_checkbox', 0, type=int))
        self.restrict_by_custom_date_checkbox.setChecked(self.settings.value('restrict_by_custom_date_checkbox', False,
                                                                             type=bool))
        self.custom_date = self.settings.value('settings_custom_date', 0, type=int)
        self.restrict_to_score_checkbox.setCheckState(self.settings.value('restrict_to_score_checkbox', 0, type=int))
        self.sub_sort_hot_radio.setChecked(self.settings.value('sub_sort_hot_radio', False, type=bool))
        self.sub_sort_rising_radio.setChecked(self.settings.value('sub_sort_rising_radio', False, type=bool))
        self.sub_sort_controversial_radio.setChecked(self.settings.value('sub_sort_controversial_radio', False,
                                                                         type=bool))
        self.sub_sort_new_radio.setChecked(self.settings.value('sub_sort_new_radio', False, type=bool))
        self.sub_sort_top_radio.setChecked(self.settings.value('sub_sort_top_radio', False, type=bool))
        self.post_score_limit_spin_box.setValue(self.settings.value('post_score_limit_spinbox', 0, type=int))
        self.post_limit_spinbox.setValue(self.settings.value('post_limit_spinbox', 25, type=int))
        self.link_filter_video_checkbox.setCheckState(self.settings.value('link_filter_video_checkbox', 0, type=int))
        self.link_filter_image_checkbox.setCheckState(self.settings.value('link_filter_image_checkbox', 0, type=int))
        self.link_filter_avoid_duplicates_checkbox.setCheckState(self.settings.value('link_filter_avoid_duplicates_'
                                                                                     'checkbox', 0, type=int))
        self.save_directory_line_edit.setText(self.settings.value('save_directory_line_edit', "", type=str))

        self.post_score_combo.addItems(('Greater Than', 'Less Than'))  # 0: Greather than, 1: Less than
        self.post_score_combo.setCurrentIndex(self.settings.value('post_score_combo', 0, type=int))
        if self.restrict_to_score_checkbox.isChecked():
            self.post_score_combo.setDisabled(False)
            self.post_score_limit_spin_box.setDisabled(False)
            self.post_score_method = self.post_score_combo.currentIndex()
        else:
            self.post_score_combo.setDisabled(True)
            self.post_score_limit_spin_box.setDisabled(True)

        # Controls for the date restriction portion of the settings
        self.restrict_date = self.date_restriction_checkbox.isChecked()
        self.date_restriction_checkbox.stateChanged.connect(self.date_restriction_checkbox_change)
        self.date_limit_edit.setDateTime(datetime.datetime.fromtimestamp(self.custom_date))
        self.restrict_by_custom_date_checkbox.stateChanged.connect(self.restrict_by_custom_date_checkbox_change)
        if self.date_restriction_checkbox.isChecked():
            self.date_limit_edit.setEnabled(False)
        else:
            self.date_limit_edit.setEnabled(True)

        self.set_post_limit = self.post_limit_spinbox.value()
        self.subreddit_sort_method = 0  # new: 0, top: 1, hot: 2, rising: 3, controversial: 4
        self.sub_sort_top_combo.addItems(('Hour', 'Day', 'Week', 'Month', 'Year', 'All Time'))
        self.sub_sort_top_combo.setCurrentIndex(self.settings.value('sub_sort_top_combo', 0, type=int))
        if self.sub_sort_top_radio.isChecked():
            self.sub_sort_top_combo.setDisabled(False)
        else:
            self.sub_sort_top_combo.setDisabled(True)
        self.sub_sort_top_method = self.sub_sort_top_combo.currentIndex()

        self.subreddit_save_by_combo.addItems(('Subreddit Name', 'User Name', 'Subreddit Name/User Name',
                                               'User Name/Subreddit Name'))
        self.subreddit_save_by_combo.setCurrentIndex(self.settings.value('subreddit_save_by_combo', 0, type=int))
        self.name_downloads_by_combo.addItems(('Image/Album Id', 'Post Title'))
        self.name_downloads_by_combo.setCurrentIndex(self.settings.value('name_downloads_by_combo', 0, type=int))

        self.list_sort_combo.addItems(('Name', 'Date Added', 'Number of Downloads'))
        self.list_sort_order_combo.addItems(('Ascending', 'Descending'))
        self.list_sort_combo.setCurrentIndex(self.settings.value('list_sort_combo', 0, type=int))
        self.list_sort_order_combo.setCurrentIndex(self.settings.value('list_sort_order_combo', 0, type=int))
        self.list_sort_method = (self.list_sort_combo.currentIndex(), self.list_sort_order_combo.currentIndex())

    def set_imgur_client(self):
        """Opens the imgur client dialog box"""
        imgur_dialog = ImgurClientDialog()
        dialog = imgur_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.imgur_client_id = imgur_dialog.client_id_line_edit.text()
            self.imgur_client_secret = imgur_dialog.client_secret_line_edit.text()

    """
    def set_reddit_account(self):
        reddit_account_dialog = RedditAccountDialog()
        dialog = reddit_account_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.reddit_account_username = reddit_account_dialog.username_line_edit.text()
            self.reddit_account_password = reddit_account_dialog.password_line_edit.text()
    """

    def backup_save_file(self):
        """Makes a copy of the programs save_file data and moves it to the specified location"""
        folder_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory", "%s%s" %
                                                                     (os.path.expanduser('~'), '/Downloads/')))
        if folder_name != "":
            reply = QtWidgets.QMessageBox.information(self, "Backup File", "Backup settings file to selected location?",
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Ok:
                shutil.copy('save_file.dat', folder_name)

    def import_backup_file(self):
        """Imports a copy of the programs save_file data to the current directory for use by the program"""
        file_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup File To Import", "%s%s" %
                                                                   (os.path.expanduser('~'), '/Downloads/')))
        try:
            if file_name != "":
                reply = QtWidgets.QMessageBox.warning(self, "Backup File", "Are you sure you want to import this save file?"
                                                                           " any existing data (user/subreddit lists, etc.)"
                                                                           " will be deleted.",
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
                if reply == QtWidgets.QMessageBox.Ok:
                    shutil.copy(file_name, os.getcwd())
                else:
                    pass
        except PermissionError:
            reply = QtWidgets.QMessageBox.warning(self, "Backup File", "Permission Denied: the file did not import "
                                                                       "please make sure you are authorized to make "
                                                                       "changes to this OS user account",
                                                  QtWidgets.QMessageBox.Ok)
            if reply == QtWidgets.QMessageBox.Ok:
                pass
            else:
                pass

    def restrict_score_shift(self):
        """Disables certain features if the current options disallow their use"""
        if self.restrict_to_score_checkbox.isChecked():
            self.post_score_combo.setDisabled(False)
            self.post_score_limit_spin_box.setDisabled(False)
        else:
            self.post_score_combo.setDisabled(True)
            self.post_score_limit_spin_box.setDisabled(True)

    def subreddit_sort_change(self):
        """Sets the sub_sort_method to the corrent int"""
        if self.sub_sort_new_radio.isChecked():
            self.subreddit_sort_method = 0
        elif self.sub_sort_top_radio.isChecked():
            self.subreddit_sort_method = 1
        elif self.sub_sort_hot_radio.isChecked():
            self.subreddit_sort_method = 2
        elif self.sub_sort_rising_radio.isChecked():
            self.subreddit_sort_method = 3
        elif self.sub_sort_controversial_radio.isChecked():
            self.subreddit_sort_method = 4

    def sub_sort_top_change(self):
        """If the sub sort method is not "top" this disables the top sort options"""
        if self.sub_sort_top_radio.isChecked():
            self.sub_sort_top_combo.setDisabled(False)
        else:
            self.sub_sort_top_combo.setDisabled(True)

    def select_save_path(self):
        """Opens a file dialog to select the save path"""
        folder_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Save Folder',"%s%s" %
                                                                     (os.path.expanduser('~'), '/Downloads/')))
        if folder_name != '':
            self.save_directory_line_edit.setText(folder_name + '/')

    def date_restriction_checkbox_change(self):
        """
        Disables an enables the date limit edit depending on the setting and also disables and enables the
        restrict_by_custom_date_checkbox depending on the setting
        """
        if self.date_restriction_checkbox.isChecked():
            self.restrict_by_custom_date_checkbox.setChecked(False)
            self.date_limit_edit.setEnabled(False)
        else:
            self.date_limit_edit.setEnabled(True)

    def restrict_by_custom_date_checkbox_change(self):
        if self.restrict_by_custom_date_checkbox.isChecked():
            self.date_restriction_checkbox.setChecked(False)

    """
    def change_page_right(self):
        current_index = self.stackedWidget.currentIndex()
        if current_index < 2:
            self.stackedWidget.setCurrentIndex(current_index + 1)
        else:
            self.stackedWidget.setCurrentIndex(0)

    def change_page_left(self):
        current_index = self.stackedWidget.currentIndex()
        if current_index > 0:
            self.stackedWidget.setCurrentIndex(current_index - 1)
        else:
            self.stackedWidget.setCurrentIndex(2)
    """

    def accept(self):
        if self._restore_defaults:
            ret = Message.restore_defaults_warning(self)
        else:
            ret = True

        if ret:
            self.set_post_limit = self.post_limit_spinbox.value()
            self.restrict_download_by_score = self.restrict_to_score_checkbox.isChecked()
            if self.restrict_download_by_score:
                self.post_score_method = self.post_score_combo.currentIndex()
            self.subreddit_sort_change()
            self.sub_sort_top_method = self.sub_sort_top_combo.currentIndex()

            if self.restrict_by_custom_date_checkbox.isChecked():
                self.custom_date = int(time.mktime(time.strptime(self.date_limit_edit.text(), '%m/%d/%Y %H:%M:%S')))
            else:
                self.custom_date = 0

            self.list_sort_method = (self.list_sort_combo.currentIndex(), self.list_sort_order_combo.currentIndex())

            self.settings.setValue('imgur_client_id', self.imgur_client_id)
            self.settings.setValue('imgur_client_secret', self.imgur_client_secret)
            self.settings.setValue('reddit_account_username', self.reddit_account_username)
            self.settings.setValue('reddit_account_password', self.reddit_account_password)
            self.settings.setValue('auto_save_checkbox', self.auto_save_checkbox.checkState())
            self.settings.setValue('date_restriction_checkbox', self.date_restriction_checkbox.checkState())
            self.settings.setValue('restrict_to_score_checkbox', self.restrict_to_score_checkbox.checkState())
            self.settings.setValue('post_score_combo_text', self.post_score_combo.currentText())
            self.settings.setValue('restrict_to_score_checkbox', self.restrict_to_score_checkbox.checkState())
            self.settings.setValue('sub_sort_hot_radio', self.sub_sort_hot_radio.isChecked())
            self.settings.setValue('sub_sort_rising_radio', self.sub_sort_rising_radio.isChecked())
            self.settings.setValue('sub_sort_controversial_radio', self.sub_sort_controversial_radio.isChecked())
            self.settings.setValue('sub_sort_new_radio', self.sub_sort_new_radio.isChecked())
            self.settings.setValue('sub_sort_top_radio', self.sub_sort_top_radio.isChecked())
            self.settings.setValue('sub_sort_top_combo', self.sub_sort_top_combo.currentIndex())
            self.settings.setValue('post_score_combo', self.post_score_combo.currentIndex())
            self.settings.setValue('post_score_limit_spinbox', self.post_score_limit_spin_box.value())
            self.settings.setValue('post_limit_spinbox', self.post_limit_spinbox.value())
            self.settings.setValue('link_filter_video_checkbox', self.link_filter_video_checkbox.checkState())
            self.settings.setValue('link_filter_image_checkbox', self.link_filter_image_checkbox.checkState())
            self.settings.setValue('link_filter_avoid_duplicates_checkbox',
                                   self.link_filter_avoid_duplicates_checkbox.checkState())
            self.settings.setValue('subreddit_save_by_combo', self.subreddit_save_by_combo.currentIndex())
            self.settings.setValue('name_downloads_by_combo', self.name_downloads_by_combo.currentIndex())
            self.settings.setValue('save_directory_line_edit', self.save_directory_line_edit.text())
            self.settings.setValue('restrict_by_custom_date_checkbox', self.restrict_by_custom_date_checkbox.isChecked())
            self.settings.setValue('settings_custom_date', self.custom_date)
            self.settings.setValue('list_sort_combo', self.list_sort_combo.currentIndex())
            self.settings.setValue('list_sort_order_combo', self.list_sort_order_combo.currentIndex())
            super().accept()

    def restore_defaults(self):
        self.auto_save_checkbox.setChecked(False)
        self.restrict_to_score_checkbox.setChecked(False)
        self.restrict_score_shift()
        self.sub_sort_hot_radio.setChecked(True)
        self.subreddit_sort_change()
        self.sub_sort_top_change()
        self.sub_sort_top_combo.setCurrentIndex(0)
        default_directory = ''.join([x if x != '\\' else '/' for x in
                                     ("%s%s" % (os.path.expanduser('~'), '/Downloads/'))])
        self.save_directory_line_edit.setText(default_directory)
        self.date_restriction_checkbox.setChecked(True)
        self.date_restriction_checkbox_change()
        self.link_filter_video_checkbox.setChecked(True)
        self.link_filter_image_checkbox.setChecked(True)
        self.link_filter_avoid_duplicates_checkbox.setChecked(True)
        self.subreddit_save_by_combo.setCurrentIndex(0)
        self.name_downloads_by_combo.setCurrentIndex(0)
        self.post_limit_spinbox.setValue(25)
        self.post_score_limit_spin_box.setValue(0)
        self.post_score_combo.setCurrentIndex(0)
        self._restore_defaults = True
