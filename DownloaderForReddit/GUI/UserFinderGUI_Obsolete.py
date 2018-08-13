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
import shutil
import subprocess
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from ..Utils import Injector
from ..Core.DownloadRunner import DownloadRunner
from ..GUI.AddRedditObjectDialog import AddUserDialog
from ..GUI_Resources.UserFinderGUI_auto import Ui_user_finder_widget
from ..UserFinder import UserFinder_Obsolete
from ..Core.Messages import Message


class UserFinderGUI(QtWidgets.QDialog, Ui_user_finder_widget):

    add_user_to_list = QtCore.pyqtSignal(list)
    closed = QtCore.pyqtSignal()

    def __init__(self, all_users, main_lists, save_path, imgur_client, queue):
        """
        The GUI that sets up and runs the user finder

        :param all_users: A list of all users in every list located in the main window
        :param main_lists: A list of the main lists located in the main window
        :param save_path: The save path where the UserFinder directory will be created or is stored
        :param imgur_client: The imgur client information
        :param queue: An instance of the queue used throughout the porgram to update various parts
        """
        QtWidgets.QDialog.__init__(self)
        self.all_users = all_users
        self.main_lists = main_lists
        self.save_path = save_path
        self.imgur_client = imgur_client
        self.queue = queue

        self.running = False
        self.auto_opened = False

        self.settings_manager = Injector.get_settings_manager()

        geom = self.settings_manager.user_finder_GUI_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())

        self.setupUi(self)
        self.found_users = []

        self.stacked_widget.setCurrentIndex(0)

        self.close_dialog_button.setVisible(False)

        self.subreddit_watchlist = self.settings_manager.user_finder_subreddit_watchlist
        self.user_blacklist = self.settings_manager.user_finder_user_blacklist

        self.subreddit_watchlist.remove('filler') if 'filler' in self.subreddit_watchlist else None
        self.user_blacklist.remove('filler') if 'filler' in self.user_blacklist else None

        self.sub_sort_method = self.settings_manager.user_finder_sort_method
        self.set_sort_by_radios(self.sub_sort_method)
        self.top_sort_groupbox.changeEvent.connect(self.set_sub_sort_method)  # TODO: Check to make sure this works

        self.watchlist_score_spinbox_2.setValue(self.settings_manager.user_finder_watch_list_score_limit)
        self.watchlist_download_sample_spinbox_2.setValue(self.settings_manager.user_finder_download_sample_size)
        self.watchlist_when_run_checkbox_2.setChecked(self.settings_manager.user_finder_run_with_main)
        self.automatically_add_user_checkbox.setChecked(self.settings_manager.user_finder_auto_add_users)
        self.automatically_add_user_checkbox.stateChanged.connect(self.auto_add_users_gui_change)
        self.auto_add_users_gui_change()
        self.watchlist_add_to_list_combo_2.setCurrentIndex(self.settings_manager.user_finder_add_to_index)

        for x in self.subreddit_watchlist:
            self.sub_watchlist_listview.addItem(x)
        self.sub_watchlist_listview.sortItems()
        for y in self.user_blacklist:
            self.blacklist_users_listview.addItem(y)
        self.blacklist_users_listview.sortItems()
        for z in self.main_lists:
            self.watchlist_add_to_list_combo_2.addItem(z)

        self.watchlist_add_subreddit_button_2.clicked.connect(self.add_subreddit_dialog)
        self.watchlist_remove_subreddit_button_2.clicked.connect(self.remove_subreddit)
        self.blacklist_user_add_button_2.clicked.connect(self.add_blacklist_user_dialog)
        self.blacklist_user_remove_button_2.clicked.connect(self.remove_blacklist_user)

        self.page_change_left_button.clicked.connect(self.change_page_left)
        self.page_change_right_button.clicked.connect(self.change_page_right)
        self.close_dialog_button.clicked.connect(lambda: self.save_user_finder(True))

        self.button_box.accepted.connect(lambda: self.save_user_finder(True))
        self.button_box.rejected.connect(self.close_finder)

        self.run_finder_button_2.clicked.connect(self.run)

        # Page two----------------------------------------------------------------------------------------------------

        self.found_user_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.content_list_icons_full_width = self.settings_manager.user_finder_content_list_icons_full_width
        self.content_list_icon_size = self.settings_manager.user_finder_content_list_icon_size

        self.user_display_list = []

        try:
            self.user_folders = [x for x in os.listdir('%sUserFinder' % self.save_path) if
                                 os.path.isdir(os.path.join('%sUserFinder' % self.save_path, x))]
            for x in self.user_folders:
                if x not in self.user_display_list:
                    self.found_user_list.addItem(x)
                    self.user_display_list.append(x)
            for x in self.found_users:
                if x.name not in self.user_display_list:
                    self.found_user_list.addItem(x.name)
                    self.user_display_list.append(x.name)
        except FileNotFoundError:
            self.user_folders = []

        self.found_user_list.setCurrentRow(0)
        self.found_user_list.currentRowChanged.connect(self.setup_content_list)

        self.setup_content_list()

        self.add_selected_button.clicked.connect(self.add_found_user_to_main_list)

        self.sub_watchlist_listview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sub_watchlist_listview.customContextMenuRequested.connect(self.sub_watchlist_right_click)

        self.blacklist_users_listview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.blacklist_users_listview.customContextMenuRequested.connect(self.blacklist_users_right_click)

        self.found_user_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.found_user_list.customContextMenuRequested.connect(self.found_user_list_right_click)

        self.content_display_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.content_display_list.customContextMenuRequested.connect(self.content_display_list_right_click)

        # Page Three -------------------------------------------------------------------------------------------------

        self.found_users_label.setText('Users Found: 0')
        self.found_count = 0
        self.step_count = 0

    def set_sort_by_radios(self, method):
        radio_dict = {0: self.sub_sort_hour_radio,
                      1: self.sub_sort_day_radio,
                      2: self.sub_sort_week_radio,
                      3: self.sub_sort_month_radio,
                      4: self.sub_sort_year_radio,
                      5: self.sub_sort_all_raido}
        radio_dict[method].setChecked(True)

    def set_sub_sort_method(self):
        if self.sub_sort_hour_radio.isChecked():
            self.sub_sort_method = 0
        elif self.sub_sort_day_radio.isChecked():
            self.sub_sort_method = 1
        elif self.sub_sort_week_radio.isChecked():
            self.sub_sort_method = 2
        elif self.sub_sort_month_radio.isChecked():
            self.sub_sort_method = 3
        elif self.sub_sort_year_radio.isChecked():
            self.sub_sort_method = 4
        else:
            self.sub_sort_method = 5

    def sub_watchlist_right_click(self):
        menu = QtWidgets.QMenu()
        try:
            position = self.sub_watchlist_listview.currentRow()
            add_sub = menu.addAction('Add Subreddit')
            remove_sub = menu.addAction('Remove Subreddit')
            add_sub.triggered.connect(self.add_subreddit_dialog)
            remove_sub.triggered.connect(self.remove_subreddit)
        except AttributeError:
            add_sub = menu.addAction('Add Subreddit')
            add_sub.triggered.connect(self.add_subreddit_dialog)
        menu.exec(QtGui.QCursor.pos())

    def blacklist_users_right_click(self):
        menu = QtWidgets.QMenu()
        try:
            position = self.blacklist_users_listview.currentRow()
            add_user = menu.addAction('Add User')
            remove_user = menu.addAction('Remove User')
            add_user.triggered.connect(self.add_blacklist_user_dialog)
            remove_user.triggered.connect(self.remove_blacklist_user)
        except AttributeError:
            add_user = menu.addAction('Add User')
            add_user.triggered.connect(self.add_blacklist_user_dialog)
        menu.exec(QtGui.QCursor.pos())

    def content_display_list_right_click(self):
        self.menu = QtWidgets.QMenu()
        try:
            position = self.content_display_list.currentRow()
            open_picture = self.menu.addAction('Open In Default Picture Viewer')
            open_folder = self.menu.addAction('Open Folder')

            self.menu.addSeparator()
            self.icons_full_width = self.menu.addAction('Icons Full List Width')
            self.icons_full_width.setCheckable(True)
            self.icon_size_menu = self.menu.addMenu('Icon Size')
            self.icon_size_group = QtWidgets.QActionGroup(self)
            self.icon_size_group.setExclusive(True)

            self.icon_size_extra_small = self.icon_size_menu.addAction('Extra Small')
            self.icon_size_extra_small.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_extra_small)
            self.icon_size_small = self.icon_size_menu.addAction('Small')
            self.icon_size_small.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_small)
            self.icon_size_medium = self.icon_size_menu.addAction('Medium')
            self.icon_size_medium.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_medium)
            self.icon_size_large = self.icon_size_menu.addAction('Large')
            self.icon_size_large.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_large)
            self.icon_size_extra_large = self.icon_size_menu.addAction('Extra Large')
            self.icon_size_extra_large.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_extra_large)
            self.set_context_menu_items_checked()

            open_picture.triggered.connect(self.open_file)
            open_folder.triggered.connect(self.open_folder)
            self.icons_full_width.triggered.connect(self.set_icons_full_width)
            self.icon_size_extra_small.triggered.connect(lambda: self.set_icon_size(48))
            self.icon_size_small.triggered.connect(lambda: self.set_icon_size(72))
            self.icon_size_medium.triggered.connect(lambda: self.set_icon_size(110))
            self.icon_size_large.triggered.connect(lambda: self.set_icon_size(176))
            self.icon_size_extra_large.triggered.connect(lambda: self.set_icon_size(256))
        except AttributeError:
            print('Exception at line 238')
        self.menu.exec(QtGui.QCursor.pos())

    def set_icons_full_width(self):
        self.content_list_icons_full_width = True
        self.content_display_list.setIconSize(QtCore.QSize(self.content_display_list.width(),
                                                           self.content_display_list.width()))

    def set_icon_size(self, size):
        self.content_list_icons_full_width = False
        self.content_list_icon_size = size
        self.content_display_list.setIconSize(QtCore.QSize(size, size))

    def set_context_menu_items_checked(self):
        if self.content_list_icons_full_width:
            self.icons_full_width.setChecked(True)
        else:
            self.icons_full_width.setChecked(False)
            if self.content_list_icon_size == 48:
                self.icon_size_extra_small.setChecked(True)
            elif self.content_list_icon_size == 72:
                self.icon_size_small.setChecked(True)
            elif self.content_list_icon_size == 110:
                self.icon_size_medium.setChecked(True)
            elif self.content_list_icon_size == 176:
                self.icon_size_large.setChecked(True)
            else:
                self.icon_size_extra_large.setChecked(True)

    def found_user_list_right_click(self):
        menu = QtWidgets.QMenu()
        try:
            position = self.found_user_list.currentRow()
            add_user = menu.addAction('Add User To List')
            remove_user = menu.addAction('Remove User')
            remove_user_and_blacklist = menu.addAction('Remove and Blacklist User')
            menu.addSeparator()
            open_user_folder = menu.addAction('Open User Download Folder')
            add_user.triggered.connect(self.add_found_user_to_main_list)
            remove_user.triggered.connect(self.remove_user_from_user_found_list)
            remove_user_and_blacklist.triggered.connect(self.remove_and_blacklist_user)
            open_user_folder.triggered.connect(self.open_folder)
        except AttributeError:
            print('Exception at line 282')
        menu.exec(QtGui.QCursor.pos())

    def run(self):
        """Creates an instance of the UserFinder class and moves it to another thread"""
        self.found_user_output.clear()
        self.save_user_finder(False)
        self.running = True
        self.stacked_widget.setCurrentIndex(2)
        self.user_finder = UserFinder_Obsolete(self.subreddit_watchlist, self.user_blacklist, self.sub_sort_method,
                                               self.watchlist_score_spinbox_2.value(),
                                               self.watchlist_download_sample_spinbox_2.value(), self.all_users, self.save_path,
                                               self.imgur_client, self.user_folders)

        self.thread = QtCore.QThread()
        self.user_finder.moveToThread(self.thread)
        self.thread.started.connect(self.user_finder.validate_subreddits)
        self.user_finder.steps.connect(self.setup_progress_bar)
        self.user_finder.step_complete.connect(self.update_progress_bar)
        self.user_finder.user_found.connect(self.add_found_user)
        self.user_finder.update_output.connect(self.update_output_box)
        self.user_finder.remove_invalid_subreddit.connect(self.remove_invalid_subreddits)
        self.user_finder.finished.connect(self.thread.quit)
        self.user_finder.finished.connect(self.user_finder.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        if not self.automatically_add_user_checkbox.isChecked():
            self.thread.finished.connect(self.download_user_samples)
        else:
            self.thread.finished.connect(self.auto_add_users_to_main_list)
        self.thread.start()

    def download_user_samples(self):
        """
        Creates an instance of the DownloadRunner class and moves it to another thread where it then downloads the
        specified number of posts from the found users
        """
        if len(self.found_users) > 0 and self.watchlist_download_sample_spinbox_2.value() > 0:
            self.found_user_output.append('Starting Download\n')

            self.reddit_extractor = DownloadRunner(self.found_users, None, self.queue,
                                                   self.watchlist_download_sample_spinbox_2.value(), self.save_path,
                                                   None, None, False, False, None, None, None)

            self.user_finder_download_thread = QtCore.QThread()
            self.reddit_extractor.moveToThread(self.user_finder_download_thread)
            self.user_finder_download_thread.started.connect(self.reddit_extractor.validate_users)
            self.reddit_extractor.finished.connect(self.user_finder_download_thread.quit)
            self.reddit_extractor.finished.connect(self.reddit_extractor.deleteLater)
            self.user_finder_download_thread.finished.connect(self.user_finder_download_thread.deleteLater)
            self.user_finder_download_thread.finished.connect(self.download_finished)
            self.user_finder_download_thread.start()
        elif len(self.found_users) > 0 >= self.watchlist_download_sample_spinbox_2.value():
            pass
        else:
            self.found_user_output.append('No users found that meet criteria\n')
            self.download_finished()

    def download_finished(self):
        """Emits the finished signal and toggles various parts of the GUI when the download has finished"""
        self.found_user_output.append('Finished')
        self.running = False
        self.user_folders = [x for x in os.listdir('%sUserFinder' % self.save_path) if
                             os.path.isdir(os.path.join('%sUserFinder' % self.save_path, x))]
        for x in self.user_folders:
            if x not in self.found_users and x not in self.user_display_list:
                self.found_user_list.addItem(x)
        self.found_user_list.sortItems()
        self.setup_content_list()
        if self.auto_opened:
            self.display_close_button()

    def remove_invalid_subreddits(self, sub):
        """If a subreddit in the list is found to not be valid, this removes the subreddit if the user wants to do so"""
        if Message.subreddit_not_valid(self, sub):
            current_row = self.subreddit_watchlist.index(sub)
            self.subreddit_watchlist.remove(sub)
            self.sub_watchlist_listview.takeItem(current_row)

    def add_subreddit_dialog(self):
        """
        Opens a dialog to add a subreddit.  The dialog is an instance of the AddUserDialog repurposed in this
        instance to add subreddits
        """
        add_sub_dialog = AddUserDialog()
        add_sub_dialog.setWindowTitle('Add Subreddit Dialog')
        add_sub_dialog.label.setText('Enter a new subreddit:')
        add_sub_dialog.add_another_button.clicked.connect(lambda: self.add_subreddit(add_sub_dialog.name))
        dialog = add_sub_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.add_subreddit(add_sub_dialog.name)

    def add_subreddit(self, new_sub):
        """Adds the subreddit entered into the dialog to the subreddit list"""
        if new_sub != '' and ' ' not in new_sub:
            if any(new_sub.lower() == name.lower() for name in self.subreddit_watchlist):
                Message.name_in_list(self)
            else:
                self.subreddit_watchlist.append(new_sub)
                self.sub_watchlist_listview.addItem(new_sub)
                self.sub_watchlist_listview.sortItems()
        else:
            Message.not_valid_name(self)

    def remove_subreddit(self):
        current_item = self.sub_watchlist_listview.currentRow()
        self.subreddit_watchlist.remove(self.subreddit_watchlist[current_item])
        self.sub_watchlist_listview.takeItem(current_item)

    def add_blacklist_user_dialog(self):
        add_user_dialog = AddUserDialog()
        add_user_dialog.add_another_button.clicked.connect(lambda: self.add_blacklist_user(add_user_dialog.name))
        dialog = add_user_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.add_blacklist_user(add_user_dialog.name)

    def add_blacklist_user(self, new_user):
        if new_user != '' and ' ' not in new_user:
            if any(new_user.lower() == name.lower() for name in self.user_blacklist):
                Message.name_in_list(self)
            else:
                self.user_blacklist.append(new_user)
                self.blacklist_users_listview.addItem(new_user)
                self.blacklist_users_listview.sortItems()
        else:
            Message.not_valid_name(self)

    def remove_blacklist_user(self):
        current_item = self.blacklist_users_listview.currentRow()
        self.user_blacklist.remove(self.user_blacklist[current_item])
        self.blacklist_users_listview.takeItem(current_item)

    def top_sort_method(self):
        if self.sub_sort_hour_radio.isChecked():
            return 0
        elif self.sub_sort_day_radio.isChecked():
            return 1
        elif self.sub_sort_week_radio.isChecked():
            return 2
        elif self.sub_sort_month_radio.isChecked():
            return 3
        elif self.sub_sort_year_radio.isChecked():
            return 4
        else:
            return 5

    def add_found_user_to_main_list(self):
        """Adds the selected found user to the specified main window user list"""
        user = self.user_folders[self.found_user_list.currentRow()]
        folder_path = '%sUserFinder/%s' % (self.save_path, user)
        self.add_user_to_list.emit([user, self.watchlist_add_to_list_combo_2.currentText()])
        self.found_user_list.takeItem(self.found_user_list.currentRow())
        shutil.rmtree(folder_path)

    def auto_add_users_to_main_list(self):
        """If the appropriate checkbox is checked this will automatically add users to the specified user list"""
        for user in self.found_users:
            self.add_user_to_list.emit([user.name, self.watchlist_add_to_list_combo_2.currentText()])
        self.download_finished()

    def auto_add_users_gui_change(self):
        if self.automatically_add_user_checkbox.isChecked():
            self.label.setEnabled(False)
            self.watchlist_download_sample_spinbox_2.setEnabled(False)
            self.label_9.setEnabled(False)
        else:
            self.label.setEnabled(True)
            self.watchlist_download_sample_spinbox_2.setEnabled(True)
            self.label_9.setEnabled(True)

    def remove_user_from_user_found_list(self):
        user = self.user_folders[self.found_user_list.currentRow()]
        folder_path = '%sUserFinder/%s' % (self.save_path, user)
        self.found_user_list.takeItem(self.found_user_list.currentRow())
        shutil.rmtree(folder_path)

    def remove_and_blacklist_user(self):
        user = self.user_folders[self.found_user_list.currentRow()]
        self.add_blacklist_user(user)
        self.remove_user_from_user_found_list()

    def setup_content_list(self):
        """
        Sets up the content display list to show the picture content located in the selected users sub directory inside
        UserFinder directory
        """
        self.content_display_list.clear()
        if self.content_list_icons_full_width:
            icon_size = self.content_display_list.width()
        else:
            icon_size = self.content_list_icon_size
        self.content_display_list.setIconSize(QtCore.QSize(icon_size, icon_size))
        try:
            index = self.found_user_list.currentRow()
        except TypeError:
            index = 0
        if len(self.user_folders) > 0:
            for file in os.listdir('%sUserFinder/%s' % (self.save_path, self.user_folders[index])):
                file_path = '%sUserFinder/%s/%s' % (self.save_path, self.user_folders[index], file)
                item = QtWidgets.QListWidgetItem()
                icon = QtGui.QIcon()
                pixmap = QtGui.QPixmap(file_path).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)
                icon.addPixmap(pixmap)
                item.setIcon(icon)
                item.setText(str(file))
                self.content_display_list.addItem(item)
                QtWidgets.QApplication.processEvents()

    def setup_progress_bar(self, status):
        if type(status) == int:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(status)
        elif status.startswith('Downloaded'):
            text, number = status.rsplit('  ', 1)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(int(number))
            self.progress_bar.setValue(0)

    def update_progress_bar(self):
        self.step_count += 1
        self.progress_bar.setValue(self.step_count)

    def update_output_box(self, text):
        self.found_user_output.append(text)

    def add_found_user(self, user):
        self.found_users.append(user)
        self.found_count += 1
        self.found_users_label.setText('Users Found: %s' % self.found_count)

    def change_page_right(self):
        right_limit = 2 if self.running else 1
        current_index = self.stacked_widget.currentIndex()
        if current_index < right_limit:
            self.stacked_widget.setCurrentIndex(current_index + 1)
        else:
            self.stacked_widget.setCurrentIndex(0)

    def change_page_left(self):
        page_limit = 2 if self.running else 1
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
        else:
            self.stacked_widget.setCurrentIndex(page_limit)

    def closeEvent(self, QCloseEvent):
        if self.running:
            if Message.downloader_running_warning(self):
                try:
                    self.thread.terminate()
                except AttributeError:
                    pass
                try:
                    self.user_finder_download_thread.terminate()
                except AttributeError:
                    pass
                self.close_finder()
            else:
                QCloseEvent.ignore()
        else:
            self.close_finder()

    def close_finder(self):
        self.settings.setValue('content_list_icons_full_width', self.content_list_icons_full_width)
        self.settings.setValue('content_list_icon_size', self.content_list_icon_size)
        self.closed.emit()
        self.close()

    def resizeEvent(self, event):
        if self.content_list_icons_full_width:
            self.content_display_list.setIconSize(QtCore.QSize(self.content_display_list.width(),
                                                               self.content_display_list.width()))

    def save_user_finder(self, close):
        self.settings_manager.user_finder_GUI_geom = self.saveGeometry()
        self.settings_manager.user_finder_subreddit_watchlist = self.subreddit_watchlist
        self.settings_manager.user_finder_user_blacklist = self.user_blacklist
        self.settings_manager.user_finder_sort_method = self.sub_sort_method
        self.settings_manager.user_finder_watch_list_score_limit = self.watchlist_score_spinbox_2.value()
        self.settings_manager.user_finder_download_sample_size = self.watchlist_download_sample_spinbox_2.value()
        self.settings_manager.user_finder_run_with_main = self.watchlist_when_run_checkbox_2.isChecked()
        self.settings_manager.user_finder_auto_add_users = self.automatically_add_user_checkbox.isChecked()
        self.settings_manager.user_finder_add_to_index = self.watchlist_add_to_list_combo_2.currentIndex()
        self.settings_manager.save_user_settings_dialog()

        if close:
            self.closed.emit()
            super().accept()

    def open_file(self):
        parent = '%sUserFinder/%s' % (self.save_path, self.user_folders[self.found_user_list.currentRow()])
        sub_directory = os.listdir(parent)
        file = '%s/%s' % (parent, sub_directory[self.content_display_list.currentRow()])

        if sys.platform == 'win32':
            os.startfile(file)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, file])

    def open_folder(self):
        folder = '%sUserFinder/%s' % (self.save_path, self.user_folders[self.found_user_list.currentRow()])

        if sys.platform == 'win32':
            os.startfile(folder)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, folder])

    def display_close_button(self):
        self.close_dialog_button.setVisible(True)
        self.close_dialog_button.setDefault(True)
