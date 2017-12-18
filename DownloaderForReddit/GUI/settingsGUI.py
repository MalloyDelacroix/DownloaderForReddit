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


import datetime
import os
import time
from PyQt5 import QtWidgets, QtCore

from GUI_Resources.DownloaderForRedditSettingsGUI_auto import Ui_SettingsGUI
import Core.Injector
from Core.Messages import Message
from GUI.ImgurClientDialog import ImgurClientDialog


class RedditDownloaderSettingsGUI(QtWidgets.QDialog, Ui_SettingsGUI):

    def __init__(self):
        """
        A dialog class where various options in the application are set
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self._restore_defaults = False

        self.sub_sort_radio_dict = {
            'NEW': self.sub_sort_new_radio,
            'TOP': self.sub_sort_top_radio,
            'HOT': self.sub_sort_hot_radio,
            'RISING': self.sub_sort_rising_radio,
            'CONTROVERSIAL': self.sub_sort_controversial_radio
        }

        self.sub_sort_top_str_dict = {
            'Hour': 'HOUR',
            'Day': 'DAY',
            'Week': 'WEEK',
            'Month': 'MONTH',
            'Year': 'YEAR',
            'All Time': 'ALL'
        }

        self.score_operator_dict = {'Greater Than': 'GREATER', 'Less Than': 'LESS'}

        self.nsfw_filter_dict = {
            'Include': 'INCLUDE',
            'Do Not Include': 'EXCLUDE',
            'Include Only NSFW': 'ONLY'
        }

        self.settings_manager = Core.Injector.get_settings_manager()

        geom = self.settings_manager.settings_dialog_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())

        self.reddit_account_link_button.setVisible(False)
        self.reddit_account_link_button.setEnabled(False)

        self.save_cancel_button_box.accepted.connect(self.accept)
        self.save_cancel_button_box.rejected.connect(self.close)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.imgur_client_button.clicked.connect(self.set_imgur_client)

        self.restrict_to_score_checkbox.stateChanged.connect(self.restrict_score_shift)
        self.sub_sort_top_radio.toggled.connect(self.sub_sort_top_change)

        self.save_directory_dialog_button.clicked.connect(self.select_save_path)

        self.imgur_client_id = self.settings_manager.imgur_client_id
        self.imgur_client_secret = self.settings_manager.imgur_client_secret
        self.auto_save_checkbox.setCheckState(self.settings_manager.auto_save)

        self.post_limit_spinbox.setValue(self.settings_manager.post_limit)

        self.restrict_to_score_checkbox.setChecked(self.settings_manager.restrict_by_score)
        self.post_score_combo.addItems(self.score_operator_dict.keys())
        for key, value in self.score_operator_dict.items():
            if value == self.settings_manager.score_limit_operator:
                self.post_score_combo.setCurrentText(key)

        if self.settings_manager.restrict_by_score:
            self.post_score_combo.setDisabled(False)
            self.post_score_limit_spin_box.setDisabled(False)
            self.post_score_method = self.post_score_combo.currentIndex()
        else:
            self.post_score_combo.setDisabled(True)
            self.post_score_limit_spin_box.setDisabled(True)
        self.post_score_limit_spin_box.setValue(self.settings_manager.post_score_limit)

        self.sub_sort_radio_dict[self.settings_manager.subreddit_sort_method].setChecked(True)

        # Controls for the date restriction portion of the settings
        self.date_restriction_checkbox.setChecked(self.settings_manager.restrict_by_date)
        self.date_restriction_checkbox.stateChanged.connect(self.date_restriction_checkbox_change)
        self.date_limit_edit.setDateTime(datetime.datetime.fromtimestamp(self.settings_manager.custom_date))
        self.restrict_by_custom_date_checkbox.setChecked(self.settings_manager.restrict_by_custom_date)
        self.restrict_by_custom_date_checkbox.stateChanged.connect(self.restrict_by_custom_date_checkbox_change)
        if self.date_restriction_checkbox.isChecked():
            self.date_limit_edit.setEnabled(False)
        else:
            self.date_limit_edit.setEnabled(True)

        self.link_filter_video_checkbox.setChecked(self.settings_manager.download_videos)
        self.link_filter_image_checkbox.setChecked(self.settings_manager.download_images)
        self.link_filter_avoid_duplicates_checkbox.setChecked(self.settings_manager.avoid_duplicates)

        self.nsfw_filter_combo.addItems(self.nsfw_filter_dict.keys())
        for key, value in self.nsfw_filter_dict.items():
            if value == self.settings_manager.nsfw_filter:
                self.nsfw_filter_combo.setCurrentText(key)

        self.save_directory_line_edit.setText(self.settings_manager.save_directory)

        self.sub_sort_top_combo.addItems(self.sub_sort_top_str_dict.keys())
        for key, value in self.sub_sort_top_str_dict.items():
            if value == self.settings_manager.subreddit_sort_top_method:
                self.sub_sort_top_combo.setCurrentText(key)
        if self.sub_sort_top_radio.isChecked():
            self.sub_sort_top_combo.setDisabled(False)
        else:
            self.sub_sort_top_combo.setDisabled(True)

        self.subreddit_save_by_combo.addItems(('Subreddit Name', 'User Name', 'Subreddit Name/User Name',
                                               'User Name/Subreddit Name'))
        self.subreddit_save_by_combo.setCurrentText(self.settings_manager.save_subreddits_by)
        self.name_downloads_by_combo.addItems(('Image/Album Id', 'Post Title'))
        self.name_downloads_by_combo.setCurrentText(self.settings_manager.name_downloads_by)

        self.thread_limit_spinbox.setValue(self.settings_manager.max_download_thread_count)
        self.thread_limit_spinbox.setMaximum(QtCore.QThread.idealThreadCount())

        self.save_undownloaded_content_checkbox.setChecked(self.settings_manager.save_undownloaded_content)

        self.total_files_downloaded_label.setText("Total Files Downloaded: " +
                                                  str(self.settings_manager.total_files_downloaded))

        self.save_directory_line_edit.setToolTip(self.save_directory_line_edit.text())

    def set_imgur_client(self):
        """Opens the imgur client dialog box"""
        imgur_dialog = ImgurClientDialog()
        imgur_dialog.client_id_line_edit.setText(self.imgur_client_id)
        imgur_dialog.client_secret_line_edit.setText(self.imgur_client_secret)
        dialog = imgur_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.imgur_client_id = imgur_dialog.client_id_line_edit.text()
            self.imgur_client_secret = imgur_dialog.client_secret_line_edit.text()

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

        folder_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Save Folder',
                                                                     self.get_default_folder()))
        if folder_name != '':
            self.save_directory_line_edit.setText(folder_name + '/')

    def get_default_folder(self):
        text = self.save_directory_line_edit.text()
        if text != '' and text != ' ':
            return text.rsplit('/', 1)[0]
        else:
            return '%s/%s/' % (os.path.expanduser('~'), 'Downloads')

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

    def accept(self):
        if self._restore_defaults:
            ret = Message.restore_defaults_warning(self)
        else:
            ret = True

        if ret:
            self.save_settings()
            super().accept()

    def closeEvent(self, QCloseEvent):
        self.settings_manager.settings_dialog_geom = self.saveGeometry()
        self.settings_manager.save_settings_dialog()

    def save_settings(self):
        self.settings_manager.imgur_client_id = self.imgur_client_id
        self.settings_manager.imgur_client_secret = self.imgur_client_secret
        self.settings_manager.auto_save = self.auto_save_checkbox.isChecked()

        self.settings_manager.restrict_by_score = self.restrict_to_score_checkbox.isChecked()
        self.settings_manager.score_limit_operator = self.score_operator_dict[self.post_score_combo.currentText()]
        self.settings_manager.post_score_limit = self.post_score_limit_spin_box.value()

        self.settings_manager.restrict_by_date = self.date_restriction_checkbox.isChecked()
        self.settings_manager.restrict_by_custom_date = self.restrict_by_custom_date_checkbox.isChecked()
        self.settings_manager.custom_date = int(time.mktime(time.strptime(self.date_limit_edit.text(),
                                                                          '%m/%d/%Y %I:%M %p')))

        self.settings_manager.subreddit_sort_method = self.get_sort_by_method()
        self.settings_manager.subreddit_sort_top_method = \
            self.sub_sort_top_str_dict[self.sub_sort_top_combo.currentText()]

        self.settings_manager.post_limit = self.post_limit_spinbox.value()

        self.settings_manager.download_videos = self.link_filter_video_checkbox.isChecked()
        self.settings_manager.download_images = self.link_filter_image_checkbox.isChecked()
        self.settings_manager.avoid_duplicates = self.link_filter_avoid_duplicates_checkbox.isChecked()

        self.settings_manager.nsfw_filter = self.nsfw_filter_dict[self.nsfw_filter_combo.currentText()]

        self.settings_manager.save_subreddits_by = self.subreddit_save_by_combo.currentText()
        self.settings_manager.name_downloads_by = self.name_downloads_by_combo.currentText()

        self.settings_manager.save_directory = self.save_directory_line_edit.text()
        self.settings_manager.max_download_thread_count = self.thread_limit_spinbox.value()
        self.settings_manager.save_undownloaded_content = self.save_undownloaded_content_checkbox.isChecked()

    def get_sort_by_method(self):
        for key, value in self.sub_sort_radio_dict.items():
            if value.isChecked():
                return key

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
