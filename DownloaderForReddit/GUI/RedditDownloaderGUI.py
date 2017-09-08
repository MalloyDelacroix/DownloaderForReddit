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
import subprocess
import sys
from datetime import datetime, date

import imgurpython
from GUI.AboutDialog import AboutDialog
from GUI.DownloadedUsersDialog import DownloadedUsersDialog
from GUI.FailedDownloadsDialog import FailedDownloadsDialog
from Core.Messages import Message, UnfinishedDownloadsWarning
from PyQt5 import QtWidgets, QtCore, QtGui
from Core.RedditExtractor import RedditExtractor
from Core.RedditObjects import User, Subreddit
from GUI.SubredditSettingsDialog import SubredditSettingsDialog
from GUI.UnfinishedDownloadsDialog import UnfinishedDownloadsDialog
from GUI.UpdateDialogGUI import UpdateDialog
from Core.UpdaterChecker import UpdateChecker
from GUI.UserFinderGUI import UserFinderGUI
from GUI.UserSettingsDialog import UserSettingsDialog
from GUI.settingsGUI import RedditDownloaderSettingsGUI
import Core.Injector

from Core.ListModel import ListModel
from GUI.AddUserDialog import AddUserDialog
from GUI_Resources.RD_GUI_auto import Ui_MainWindow
from version import __version__


class RedditDownloaderGUI(QtWidgets.QMainWindow, Ui_MainWindow):

    stop_download = QtCore.pyqtSignal()
    update_user_finder = QtCore.pyqtSignal()

    def __init__(self, queue, receiver):
        """
        The main GUI window that all interaction is done through.

        :param queue: An instance of the queue initialized in the "main" function and passed to the main GUI window in
         order to update the main GUI output box
        :param receiver: The receiver that is initialized in the "main" function and moved to another thread.  This
        keeps the queue updated with fresh output from all throughout the program
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.version = __version__
        self.failed_list = []
        self.last_downloaded_users = {}
        self.download_count = 0
        self.downloaded = 0
        self.running = False
        self.user_finder_open = False

        # region Settings
        self.settings_manager = Core.Injector.get_settings_manager()

        geom = self.settings_manager.main_window_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())
        self.list_sort_method = self.settings_manager.list_sort_method
        self.list_order_method = self.settings_manager.list_order_method
        self.download_users_checkbox.setChecked(self.settings_manager.download_users)
        self.download_subreddit_checkbox.setChecked(self.settings_manager.download_subreddits)
        self.run_user_finder_auto = self.settings_manager.user_finder_run_with_main
        # endregion

        self.unfinished_downloads_available = False
        self.unfinished_downloads = None

        self.queue = queue
        self.receiver = receiver
        self.user_view_chooser_dict = {}
        self.subreddit_view_chooser_dict = {}
        self.load_state()

        self.file_add_user_list.triggered.connect(self.add_user_list)
        self.file_remove_user_list.triggered.connect(self.remove_user_list)
        self.file_add_subreddit_list.triggered.connect(self.add_subreddit_list)
        self.file_remove_subreddit_list.triggered.connect(self.remove_subreddit_list)
        self.file_failed_download_list.triggered.connect(self.display_failed_downloads)
        self.file_last_downloaded_users.triggered.connect(self.open_last_downloaded_users)
        self.file_unfinished_downloads.triggered.connect(self.display_unfinished_downloads_dialog)
        self.file_imgur_credits.triggered.connect(self.display_imgur_client_information)
        self.file_user_manual.triggered.connect(self.open_user_manual)
        self.file_check_for_updates.triggered.connect(lambda: self.check_for_updates(True))
        self.file_about.triggered.connect(self.display_about_dialog)
        self.file_user_list_count.triggered.connect(lambda: self.user_settings(0, True))
        self.file_subreddit_list_count.triggered.connect(lambda: self.subreddit_settings(0, True))

        self.list_view_group = QtWidgets.QActionGroup(self)
        self.list_view_group.addAction(self.view_sort_list_by_name)
        self.list_view_group.addAction(self.view_sort_list_by_date_added)
        self.list_view_group.addAction(self.view_sort_list_by_number_of_downloads)
        self.view_sort_list_by_name.triggered.connect(lambda: self.set_list_sort_method(0))
        self.view_sort_list_by_date_added.triggered.connect(lambda: self.set_list_sort_method(1))
        self.view_sort_list_by_number_of_downloads.triggered.connect(lambda: self.set_list_sort_method(2))

        self.list_view_order = QtWidgets.QActionGroup(self)
        self.list_view_order.addAction(self.view_order_by_ascending)
        self.list_view_order.addAction(self.view_order_by_descending)
        self.view_order_by_ascending.triggered.connect(lambda: self.set_list_order_method(0))
        self.view_order_by_descending.triggered.connect(lambda: self.set_list_order_method(1))
        self.set_view_menu_items_checked()

        self.refresh_user_count()
        self.refresh_subreddit_count()

        if not self.unfinished_downloads_available:
            self.file_unfinished_downloads.setEnabled(False)
        if len(self.last_downloaded_users) < 1:
            self.file_last_downloaded_users.setEnabled(False)
        if len(self.failed_list) < 1:
            self.file_failed_download_list.setEnabled(False)

        self.file_open_user_finder.triggered.connect(lambda: self.display_user_finder(False))

        self.file_open_settings.triggered.connect(self.open_settings_dialog)
        self.file_save.triggered.connect(self.save_state)
        self.file_exit.triggered.connect(self.close)

        self.download_button.clicked.connect(self.button_assignment)
        self.add_user_button.clicked.connect(self.add_user_dialog)
        self.remove_user_button.clicked.connect(self.remove_user)
        self.add_subreddit_button.clicked.connect(self.add_subreddit_dialog)
        self.remove_subreddit_button.clicked.connect(self.remove_subreddit)

        self.user_lists_combo.activated.connect(self.change_user_list)
        self.subreddit_list_combo.activated.connect(self.change_subreddit_list)

        self.user_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.user_list_view.customContextMenuRequested.connect(self.user_list_right_click)

        self.user_list_view.doubleClicked.connect(lambda: self.user_settings(0, False))
        self.user_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.user_lists_combo.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.user_lists_combo.customContextMenuRequested.connect(self.user_list_combo_right_click)

        self.subreddit_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subreddit_list_view.customContextMenuRequested.connect(self.subreddit_list_right_click)

        self.subreddit_list_view.doubleClicked.connect(lambda: self.subreddit_settings(0, False))
        self.subreddit_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.subreddit_list_combo.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subreddit_list_combo.customContextMenuRequested.connect(self.subreddit_list_combo_right_click)

        self.add_user_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.add_user_button.customContextMenuRequested.connect(self.add_user_button_right_click)

        self.add_subreddit_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.add_subreddit_button.customContextMenuRequested.connect(self.add_subreddit_button_right_click)

        self.progress_bar = QtWidgets.QProgressBar()
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.bar_count = 0
        self.progress_bar.setToolTip('Displays the progress of user/subreddit validation and link extraction')
        self.progress_bar.setVisible(False)
        self.progress_label = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(self.progress_label)
        self.progress_label.setText('Extraction Complete')
        self.progress_label.setVisible(False)

        self.check_for_updates(False)
        # self.check_first_run()

    def user_list_right_click(self):
        user_menu = QtWidgets.QMenu()
        try:
            position = self.get_selected_view_index(self.user_list_view).row()
            user_settings = user_menu.addAction("User Settings")
            user_downloads = user_menu.addAction("View User Downloads")
            user_menu.addSeparator()
            open_user_folder = user_menu.addAction("Open Download Folder")
            user_menu.addSeparator()
            add_user = user_menu.addAction("Add User")
            remove_user = user_menu.addAction("Remove User")
            add_user.triggered.connect(self.add_user_dialog)
            remove_user.triggered.connect(self.remove_user)
            user_settings.triggered.connect(lambda: self.user_settings(0, False))
            user_downloads.triggered.connect(lambda: self.user_settings(1, False))
            open_user_folder.triggered.connect(self.open_user_download_folder)
        except AttributeError:
            add_user = user_menu.addAction("Add User")
            add_user.triggered.connect(self.add_user_dialog)
        user_menu.exec(QtGui.QCursor.pos())

    def subreddit_list_right_click(self):
        subreddit_menu = QtWidgets.QMenu()
        try:
            position = self.get_selected_view_index(self.subreddit_list_view).row()
            subreddit_settings = subreddit_menu.addAction("Subreddit Settings")
            subreddit_downloads = subreddit_menu.addAction("View Subreddit Downloads")
            subreddit_menu.addSeparator()
            open_subreddit_folder = subreddit_menu.addAction("Open Download Folder")
            subreddit_menu.addSeparator()
            add_subreddit = subreddit_menu.addAction("Add Subreddit")
            remove_subreddit = subreddit_menu.addAction("Remove Subreddit")
            add_subreddit.triggered.connect(self.add_subreddit_dialog)
            remove_subreddit.triggered.connect(self.remove_subreddit)
            subreddit_settings.triggered.connect(lambda: self.subreddit_settings(0, False))
            subreddit_downloads.triggered.connect(lambda: self.subreddit_settings(1, False))
            open_subreddit_folder.triggered.connect(self.open_subreddit_download_folder)
        except AttributeError:
            add_subreddit = subreddit_menu.addAction("Add Subreddit")
            add_subreddit.triggered.connect(self.add_subreddit_dialog)
        subreddit_menu.exec(QtGui.QCursor.pos())

    def user_list_combo_right_click(self):
        menu = QtWidgets.QMenu()
        add_list = menu.addAction('Add User List')
        remove_list = menu.addAction('Remove User List')
        add_list.triggered.connect(self.add_user_list)
        remove_list.triggered.connect(self.remove_user_list)
        menu.exec(QtGui.QCursor.pos())

    def subreddit_list_combo_right_click(self):
        menu = QtWidgets.QMenu()
        add_list = menu.addAction('Add Subreddit List')
        remove_list = menu.addAction('Remove Subreddit List')
        add_list.triggered.connect(self.add_subreddit_list)
        remove_list.triggered.connect(self.remove_subreddit_list)
        menu.exec(QtGui.QCursor.pos())

    def add_user_button_right_click(self):
        menu = QtWidgets.QMenu()
        import_users = menu.addAction('Import Users From Folder')
        import_users.triggered.connect(self.import_user_list_from_folder)
        menu.exec(QtGui.QCursor.pos())

    def add_subreddit_button_right_click(self):
        menu = QtWidgets.QMenu()
        import_subreddits = menu.addAction('Import Subreddits From Folder')
        import_subreddits.triggered.connect(self.import_subreddit_list_from_folder)
        menu.exec(QtGui.QCursor.pos())

    def user_settings(self, page, from_menu):
        """
        Opens the user settings dialog.  A page is supplied because the right click menu option 'View User Downloads'
        will open page two of the dialog which shows the user downloads.  From menu will almost always be false, except
        when the dialog is opened from the file menu.  This is done so that a user does not have to be selected to open
        the dialog from the file menu
        """
        current_list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        # try:
        if not from_menu:
            position = self.get_selected_view_index(self.user_list_view).row()
        else:
            position = 0
        user_settings_dialog = UserSettingsDialog(current_list_model,
                                                  current_list_model.reddit_object_list[position])
        user_settings_dialog.single_download.connect(self.run_single_user)
        user_settings_dialog.show()
        if page == 1:
            user_settings_dialog.change_to_downloads_view()
        if not user_settings_dialog.closed:
            dialog = user_settings_dialog.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                if not user_settings_dialog.restore_defaults:
                    current_list_model.reddit_object_list = user_settings_dialog.user_list
                else:
                    for user in current_list_model.reddit_object_list:
                        user.custom_date_limit = None
                        user.avoid_duplicates = self.avoid_duplicates
                        user.download_videos = self.download_videos
                        user.download_images = self.download_images
                        user.do_not_edit = False
                        user.save_path = '%s%s/' % (self.save_path, user.name)
                        user.name_downloads_by = self.name_downloads_by
                        user.post_limit = self.post_limit
        # except AttributeError:
            # Message.no_user_selected(self)

    def open_user_download_folder(self):
        """Opens the Folder where the users downloads are saved using the default file manager"""
        current_list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        try:
            position = self.get_selected_view_index(self.user_list_view).row()
            selected_user = current_list_model.reddit_object_list[position]
            download_folder = selected_user.save_path
            if sys.platform == 'win32':
                os.startfile(download_folder)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, download_folder])
        except AttributeError:
            Message.no_user_selected(self)
        except FileNotFoundError:
            Message.no_user_download_folder(self)

    def subreddit_settings(self, page, from_menu):
        """Operates the same as the user_settings function"""
        current_list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            if not from_menu:
                position = self.get_selected_view_index(self.subreddit_list_view).row()
            else:
                position = 0
            subreddit_settings_dialog = SubredditSettingsDialog(current_list_model,
                                                                current_list_model.reddit_object_list[position])
            subreddit_settings_dialog.single_download.connect(self.run_single_subreddit)
            subreddit_settings_dialog.show()
            if page == 1:
                subreddit_settings_dialog.change_to_downloads_view()
            if not subreddit_settings_dialog.closed:
                dialog = subreddit_settings_dialog.exec_()
                if dialog == QtWidgets.QDialog.Accepted:
                    if not subreddit_settings_dialog.restore_defaults:
                        current_list_model.reddit_object_list = subreddit_settings_dialog.subreddit_list
                    else:
                        for sub in current_list_model.reddit_object_list:
                            sub.custom_date_limit = None
                            sub.avoid_duplicates = self.avoid_duplicates
                            sub.download_videos = self.download_videos
                            sub.download_images = self.download_images
                            sub.do_not_edit = False
                            sub.save_path = self.save_path
                            sub.name_downloads_by = self.name_downloads_by
                            sub.post_limit = self.post_limit
        except AttributeError:
            Message.no_subreddit_selected(self)

    def open_subreddit_download_folder(self):
        """Opens the Folder where the subreddit downloads are saved using the default file manager"""
        current_list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            position = self.get_selected_view_index(self.subreddit_list_view).row()
            selected_sub = current_list_model.reddit_object_list[position]
            download_folder = '%s%s/' % (selected_sub.save_path, selected_sub.name.lower())
            if sys.platform == 'win32':
                os.startfile(download_folder)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, download_folder])
        except AttributeError:
            Message.no_subreddit_selected(self)
        except FileNotFoundError:
            Message.no_subreddit_download_folder(self)

    def button_assignment(self):
        """Assigns what the download button does depending on if the downloader is currently running"""
        if not self.running:
            self.run()
        else:
            self.stop_download.emit()

    def run(self):
        """Runs the extractor with the intended settings"""
        try:
            self.failed_list.clear()
            self.started_download_gui_shift()
            if self.run_user_finder_auto:
                self.display_user_finder(True)
            if self.download_users_checkbox.isChecked() and not self.download_subreddit_checkbox.isChecked():
                self.run_user()
            elif not self.download_users_checkbox.isChecked() and self.download_subreddit_checkbox.isChecked():
                self.run_subreddit()
            elif self.download_users_checkbox.isChecked() and self.download_subreddit_checkbox.isChecked():
                self.run_user_and_subreddit()
            else:
                self.finished_download_gui_shift()
                self.update_output("You must check either the download user checkbox, the download subreddit checkbox, "
                                   "or both checkboxes.  Checking both checkboxes will constrain the user download to "
                                   "only the subreddits in the current list")
        except KeyError:
            Message.nothing_to_download(self)
            self.finished_download_gui_shift()

        """
        except:
            self.output_box.append('\nThere was an error establishing a connection. Please try again later.\n'
                                   'If the error occured after content was extracted, this content has been added to '
                                   'the previously downloaded list. To attemp to redownload this content please uncheck'
                                   ' the "avoid duplicates" checkbox in settings')
        """

    def run_user(self):
        user_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
        self.reddit_extractor = RedditExtractor(user_list, None, self.queue, None)
        self.start_reddit_extractor_thread('USER')

    def run_single_user(self, user):
        """
        Called from the user settings dialog and supplied the name of the selected user.  Downloads only the
        selected user
        """
        self.started_download_gui_shift()
        user_list = [user]
        self.reddit_extractor = RedditExtractor(user_list, None, self.queue, None)
        self.start_reddit_extractor_thread('USER')

    def run_subreddit(self):
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.reddit_extractor = RedditExtractor(None, subreddit_list, self.queue, None)
        self.start_reddit_extractor_thread('SUBREDDIT')

    def run_single_subreddit(self, subreddit):
        """
        Called from the subreddit settings dialog and supplied the name of the selected subreddit.  Downloads only the
        selected subreddit
        """
        self.started_download_gui_shift()
        subreddit_list = [subreddit]
        self.reddit_extractor = RedditExtractor(None, subreddit_list, self.queue, None)
        self.start_reddit_extractor_thread('SUBREDDIT')

    def run_user_and_subreddit(self):
        """
        Downloads from the users in the user list only the content which has been posted to the subreddits in the
        subreddit list.
        """
        user_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.reddit_extractor = RedditExtractor(user_list, subreddit_list, self.queue, None)
        self.start_reddit_extractor_thread('USERS_AND_SUBREDDITS')

    def run_unfinished_downloads(self):
        """Downloads the content that was left during the last run if the user clicked the stop download button"""
        self.download_count = 0
        self.started_download_gui_shift()
        self.reddit_extractor = RedditExtractor(None, None, self.queue, self.unfinished_downloads)
        self.start_reddit_extractor_thread('UNFINISHED')

    def start_reddit_extractor_thread(self, download_type):
        """Moves the extractor to a different thread and calls the appropriate function for the type of download"""
        self.stop_download.connect(self.reddit_extractor.stop_download)
        self.thread = QtCore.QThread()
        self.reddit_extractor.moveToThread(self.thread)
        if download_type == 'USER':
            self.thread.started.connect(self.reddit_extractor.validate_users)
        elif download_type == 'SUBREDDIT':
            self.thread.started.connect(self.reddit_extractor.validate_subreddits)
        elif download_type == 'USERS_AND_SUBREDDITS':
            self.thread.started.connect(self.reddit_extractor.validate_users_and_subreddits)
        elif download_type == 'UNFINISHED':
            self.thread.started.connect(self.reddit_extractor.finish_downloads)
        self.reddit_extractor.remove_invalid_user.connect(self.remove_invalid_user)
        self.reddit_extractor.downloaded_users_signal.connect(self.fill_downloaded_users_list)
        self.reddit_extractor.setup_progress_bar.connect(self.setup_progress_bar)
        self.reddit_extractor.update_progress_bar_signal.connect(self.update_progress_bar)
        self.reddit_extractor.unfinished_downloads_signal.connect(self.set_unfinished_downloads)
        self.reddit_extractor.finished.connect(self.thread.quit)
        self.reddit_extractor.finished.connect(self.reddit_extractor.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.finished_download_gui_shift)
        self.thread.start()

    def update_output(self, text):
        """
        Updates outputs the supplied text to the output box in the GUI.  Also supplies the content to update the status
        bar, failed download dialog box, and if the user finder is open, will emit a signal to update the user finder
        progress bar
        """
        if text.lower().startswith('failed'):
            self.failed_list.append(text)
            self.output_box.append(text)
        elif text.startswith('Saved'):
            self.update_status_bar_download_count()
            self.output_box.append(text)
        elif text.startswith('Count'):
            t, count = text.rsplit(' ', 1)
            self.download_count += int(count)
        else:
            self.output_box.append(text)

    def update_status_bar_download_count(self):
        self.downloaded += 1
        self.total_files_downloaded += 1
        self.statusbar.showMessage('Downloaded: %s  of  %s' % (self.downloaded, self.download_count), -1)

    def setup_progress_bar(self, limit):
        self.progress_bar.setVisible(True)
        if limit < 100:
            minimum = 0
            maximum = limit
        else:
            minimum = 100 - limit
            maximum = 100
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(minimum)

    def update_progress_bar(self):
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.progress_bar.value() == self.progress_bar.maximum():
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(True)

    def add_user_list(self):
        new_user_list, ok = QtWidgets.QInputDialog.getText(self, "New User List Dialog", "Enter the new user list:")
        if ok:
            if new_user_list != '':
                self.user_lists_combo.addItem(new_user_list)
                self.user_lists_combo.setCurrentText(new_user_list)
                x = ListModel(new_user_list, "user")
                self.user_view_chooser_dict[new_user_list] = x
                self.user_list_view.setModel(x)
                self.refresh_user_count()
            else:
                Message.not_valid_name(self)
        else:
            pass

    def remove_user_list(self):
        try:
            if Message.remove_user_list(self):
                current_user_list = self.user_lists_combo.currentText()
                del self.user_view_chooser_dict[current_user_list]
                self.user_lists_combo.removeItem(self.user_lists_combo.currentIndex())
                if self.user_lists_combo.currentText() != '':
                    self.user_list_view.setModel(self.user_view_chooser_dict[self.user_lists_combo.currentText()])
                    self.user_view_chooser_dict[
                        self.user_lists_combo.currentText()].sort_lists((self.list_sort_method, self.list_order_method))
                else:
                    self.user_list_view.setModel(None)
                self.refresh_user_count()
        except KeyError:
            Message.no_user_list(self)

    def change_user_list(self):
        """Changes the user list model based on the user_list_combo"""
        new_list_view = self.user_lists_combo.currentText()
        self.user_list_view.setModel(self.user_view_chooser_dict[new_list_view])
        self.user_view_chooser_dict[new_list_view].sort_lists((self.list_sort_method, self.list_order_method))
        self.refresh_user_count()

    def add_subreddit_list(self):
        new_subreddit_list, ok = QtWidgets.QInputDialog.getText(self, "New User List Dialog",
                                                                "Enter the new user list:")
        if ok:
            if new_subreddit_list != '':
                self.subreddit_list_combo.addItem(new_subreddit_list)
                self.subreddit_list_combo.setCurrentText(new_subreddit_list)
                x = ListModel(new_subreddit_list, "subreddit")
                self.subreddit_view_chooser_dict[new_subreddit_list] = x
                self.subreddit_list_view.setModel(x)
                self.refresh_subreddit_count()
            else:
                Message.not_valid_name(self)
        else:
            pass

    def remove_subreddit_list(self):
        try:
            if Message.remove_subreddit_list(self):
                current_sub_list = self.subreddit_list_combo.currentText()
                del self.subreddit_view_chooser_dict[current_sub_list]
                self.subreddit_list_combo.removeItem(self.subreddit_list_combo.currentIndex())
                if self.subreddit_list_combo.currentText() != '':
                    self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[
                                                          self.subreddit_list_combo.currentText()])
                    self.subreddit_view_chooser_dict[
                        self.subreddit_lists_combo.currentText()].sort_lists((self.list_sort_method,
                                                                              self.list_order_method))
                else:
                    self.subreddit_list_view.setModel(None)
                self.refresh_subreddit_count()
        except KeyError:
            Message.no_subreddit_list(self)

    def change_subreddit_list(self):
        new_list_view = self.subreddit_list_combo.currentText()
        self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[new_list_view])
        self.subreddit_view_chooser_dict[new_list_view].sort_lists((self.list_sort_method, self.list_order_method))
        self.refresh_subreddit_count()

    def add_user_dialog(self):
        """Opens the dialog to enter the user name"""
        if self.user_lists_combo != '' and len(self.user_view_chooser_dict) > 0:
            add_user_dialog = AddUserDialog()
            add_user_dialog.add_another_button.clicked.connect(lambda: self.add_user(add_user_dialog.name))
            dialog = add_user_dialog.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                self.add_user(add_user_dialog.name)
        else:
            Message.no_user_list(self)

    def add_found_user(self, lst):
        """Adds a user found by the user finder to the supplied list which is selected from the user finder GUI"""
        insertion_list = self.user_view_chooser_dict[lst[1]]
        new_user = lst[0]
        if any(new_user.lower() == name.lower() for name in insertion_list.display_list):
            Message.name_in_list(self)
        else:
            x = self.make_user(new_user)
            insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
            insertion_list.setData(insertion_list.rowCount() - 1, x)
        insertion_list.sort_lists((self.list_sort_method, self.list_order_method))
        self.refresh_user_count()

    def add_user(self, new_user):
        """Adds a user to the current list"""
        insertion_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        try:
            if new_user != '' and ' ' not in new_user:
                if any(new_user.lower() == name.lower() for name in insertion_list.display_list):
                    Message.name_in_list(self)
                else:
                    x = self.make_user(new_user)
                    insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
                    insertion_list.setData(insertion_list.rowCount() - 1, x)
                    insertion_list.sort_lists((self.list_sort_method, self.list_order_method))
                    self.refresh_user_count()
            else:
                Message.not_valid_name(self)

        except KeyError:
            Message.no_user_list(self)

    def make_user(self, name):
        """
        Makes a new User object
        :param name: The name of the user object
        :return: A new user object with the supplied name
        """
        new_user = User(self.version, name, self.settings_manager.save_directory, self.settings_manager.post_limit,
                 self.settings_manager.avoid_duplicates, self.settings_manager.download_videos,
                 self.settings_manager.download_images, self.settings_manager.save_subreddits_by,
                 self.settings_manager.name_downloads_by, datetime.now().timestamp())
        return new_user

    def remove_user(self):
        try:
            if Message.remove_user(self):
                working_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
                working_list.removeRows(self.get_selected_view_index(self.user_list_view).row(), 1)
                self.refresh_user_count()
            else:
                pass
        except (KeyError, AttributeError):
            Message.no_user_selected(self)

    def remove_invalid_user(self, user):
        """If a user name is not valid, this removes the user from the list"""
        if Message.user_not_valid(self, user.name):
            working_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
            working_list.reddit_object_list.remove(user)
            working_list.display_list.remove(user.name)
            if os.path.isdir(user.save_path):
                os.rename(user.save_path, '%s (deleted)' % user.save_path[:-1])
            self.refresh_user_count()

    def add_subreddit_dialog(self):
        """See add_user_dialog"""
        if self.subreddit_list_combo != '' and len(self.subreddit_view_chooser_dict) > 0:
            add_sub_dialog = AddUserDialog()
            add_sub_dialog.setWindowTitle('Add Subreddit Dialog')
            add_sub_dialog.label.setText('Enter a new subreddit:')
            add_sub_dialog.add_another_button.clicked.connect(lambda: self.add_subreddit(add_sub_dialog.name))
            dialog = add_sub_dialog.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                self.add_subreddit(add_sub_dialog.name)
        else:
            Message.no_user_list(self)

    def add_subreddit(self, new_sub):
        """See add_user"""
        insertion_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            if new_sub != '' and ' ' not in new_sub:
                if any(new_sub.lower() == name.lower() for name in insertion_list.display_list):
                    Message.name_in_list(self)
                else:
                    x = self.make_subreddit(new_sub)
                    insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
                    insertion_list.setData(insertion_list.rowCount() - 1, x)
                    insertion_list.sort_lists((self.list_sort_method, self.list_order_method))
                    self.refresh_subreddit_count()
            else:
                Message.not_valid_name(self)
        except KeyError:
            Message.no_subreddit_list(self)

    def make_subreddit(self, name):
        """
        Makes a new subreddit object
        :param name: The name of the subreddit
        :return: A new subreddit object with the supplied name
        """
        new_sub = Subreddit(self.version, name, self.settings_manager.save_directory, self.settings_manager.post_limit,
                            self.settings_manager.avoid_duplicates, self.settings_manager.download_videos,
                            self.settings_manager.download_images, self.settings_manager.save_subreddits_by,
                            self.settings_manager.name_downloads_by, datetime.now().timestamp())
        return new_sub

    def remove_subreddit(self):
        try:
            if Message.remove_subreddit(self):
                working_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
                working_list.removeRows(self.get_selected_view_index(self.subreddit_list_view).row(), 1)
                self.refresh_subreddit_count()
            else:
                pass
        except (KeyError, AttributeError):
            Message.no_subreddit_selected(self)

    def remove_invalid_subreddit(self, sub):
        """See remove_invalid_subreddit"""
        if Message.subreddit_not_valid(self, sub.name):
            working_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
            working_list.reddit_object_list.remove(sub)
            working_list.display_list.remove(sub.name)
            self.refresh_subreddit_count()

    def import_user_list_from_folder(self):
        """Opens a file dialog and then imports the names of the subfolders as users to the current user list"""
        master_folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select The Folder to Import From',
                                                                       self.save_path))
        reply = QtWidgets.QMessageBox.information(self, 'Import From Folder?',
                                                  'Import names of all subfolders from %s?' % master_folder,
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Ok:
            for folder in os.listdir(master_folder):
                self.add_user(folder)

    def import_subreddit_list_from_folder(self):
        """See import_user_list_from_folder"""
        master_folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select The Folder to Import From',
                                                                       self.save_path))
        reply = QtWidgets.QMessageBox.information(self, 'Import From Folder?',
                                                  'Import names of all subfolders from %s?' % master_folder,
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Ok:
            for folder in os.listdir(master_folder):
                self.add_subreddit(folder)

    def get_selected_view_index(self, list_view):
        """Returns a single index if multiple are selected"""
        indicies = list_view.selectedIndexes()
        index = None
        if len(indicies) > 0:
            index = indicies[0]
        return index

    def fill_downloaded_users_list(self, downloaded_user_dict):
        """Adds a users name to a list if they had content downloaded while the program is open"""
        self.last_downloaded_users = downloaded_user_dict
        self.file_last_downloaded_users.setEnabled(True)

    def open_last_downloaded_users(self):
        """
        Opens a dialog that shows the downloads of any user that has been added to the last downloaded users list.
        """
        if len(self.last_downloaded_users) > 0:
            user_display_list = [user for user in
                                 self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
                                 if user.name in self.last_downloaded_users]

            downloaded_users_dialog = DownloadedUsersDialog(user_display_list, user_display_list[0],
                                                            self.last_downloaded_users)
            downloaded_users_dialog.change_to_downloads_view()
            downloaded_users_dialog.show()
        else:
            Message.no_users_downloaded(self)

    def started_download_gui_shift(self):
        """Disables certain options in the GUI that may be problematic if used while the downloader is running"""
        self.running = True
        self.download_count = 0
        self.output_box.clear()
        self.download_button.setText('Downloading...Click to Stop Download')
        self.add_user_button.setDisabled(True)
        self.remove_user_button.setDisabled(True)
        self.add_subreddit_button.setDisabled(True)
        self.remove_subreddit_button.setDisabled(True)
        self.file_add_user_list.setDisabled(True)
        self.file_add_subreddit_list.setDisabled(True)
        self.file_remove_user_list.setDisabled(True)
        self.file_remove_subreddit_list.setDisabled(True)
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(True)

    def finished_download_gui_shift(self):
        """Re-enables disabled GUI options"""
        self.running = False
        self.download_button.setText('Download')
        self.add_user_button.setDisabled(False)
        self.remove_user_button.setDisabled(False)
        self.add_subreddit_button.setDisabled(False)
        self.remove_subreddit_button.setDisabled(False)
        self.file_add_user_list.setDisabled(False)
        self.file_add_subreddit_list.setDisabled(False)
        self.file_remove_user_list.setDisabled(False)
        self.file_remove_subreddit_list.setDisabled(False)
        self.update_number_of_downloads()
        if self.auto_display_failed_list and len(self.failed_list) > 0:
            self.display_failed_downloads()
        self.download_count = 0

    def finish_progress_bar(self):
        """
        Changes the progress bar text to show that it is complete and also moves the progress bar value to the maximum
        if for whatever reason it was not already there
        """
        self.progress_label.setText('Download complete - Downloaded: %s' % self.download_count)
        if self.progress_bar.value() < self.progress_bar.maximum():
            self.progress_bar.setValue(self.progress_bar.maximum())

    def open_settings_dialog(self):
        """Displays the main settings dialog"""
        settings = RedditDownloaderSettingsGUI()
        dialog = settings.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.update_user_settings()
            self.update_subreddit_settings()
            self.save_state()

    def update_user_settings(self):
        """Iterates through the user list and calls update settings for each user"""
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                if not user.do_not_edit:
                    self.update_object_settings(user)

    def update_subreddit_settings(self):
        """Iterates through the subreddit list and calls update settings for each sub"""
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                if not sub.do_not_edit:
                    self.update_object_settings(sub)

    def update_object_settings(self, object):
        """Updates object specific settings for the supplied object"""
        object.update_post_limit(self.settings_manager.post_limit)
        object.update_save_path(self.settings_manager.save_directory)
        object.update_name_downloads_by(self.settings_manager.name_downloads_by)
        object.update_avoid_duplicates(self.settings_manager.avoid_duplicates)
        object.update_download_videos(self.settings_manager.download_videos)
        object.update_download_images(self.settings_manager.download_images)
        self.update_custom_dates(object)

    def update_custom_dates(self, object):
        if self.settings_manager.restrict_by_custom_date:
            object.update_custom_date_limit(self.settings_manager.custom_date)
        else:
            object.update_custom_date_limit(None)

    def display_failed_downloads(self):
        """Opens a dialog with information about any content that was not able to be downloaded for whatever reason"""
        failed_dialog = FailedDownloadsDialog(self.failed_list)
        failed_dialog.auto_display_checkbox.setChecked(not self.auto_display_failed_list)
        failed_dialog.show()
        dialog = failed_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.auto_display_failed_list = not failed_dialog.auto_display_checkbox.isChecked()

    def display_user_finder(self, auto):
        """Opens the UserFinder dialog"""
        self.user_finder_open = True
        self.file_open_user_finder.setEnabled(False)
        all_existing_users = []
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                all_existing_users.append(user.name)
        user_lists = [key for key, value in self.user_view_chooser_dict.items()]
        user_finder = UserFinderGUI(all_existing_users, user_lists, self.save_path, self.imgur_client, self.queue)
        # user_finder.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        user_finder.watchlist_when_run_checkbox_2.setChecked(self.run_user_finder_auto)
        user_finder.add_user_to_list.connect(self.add_found_user)
        self.update_user_finder.connect(user_finder.update_progress_bar)
        user_finder.closed.connect(self.user_finder_closed)
        if auto:
            user_finder.auto_opened = True
            user_finder.run()
        user_finder.show()
        if user_finder.exec_() == QtWidgets.QDialog.Accepted:
            self.run_user_finder_auto = user_finder.watchlist_when_run_checkbox_2.isChecked()

    def user_finder_closed(self):
        self.user_finder_open = False
        self.file_open_user_finder.setEnabled(True)

    def update_user_finder_progress_bar(self):
        self.update_user_finder.emit()

    def set_unfinished_downloads(self, unfinished_list):
        """
        If the downloader is stopped before all content has been downloaded, this will save the list of unfinished
        downloads and enable to file menu button to open the dialog
        """
        self.unfinished_downloads = unfinished_list
        self.unfinished_downloads_available = True
        self.file_unfinished_downloads.setEnabled(True)

    def display_unfinished_downloads_dialog(self):
        try:
            unfinished_dialog = UnfinishedDownloadsDialog()
            unfinished_dialog.label.setText('You have %s unfinished downloads.  How would you like to proceed?' %
                                            len(self.unfinished_downloads))
            unfinished_dialog.download_button.clicked.connect(self.run_unfinished_downloads)
            unfinished_dialog.close_and_delete_button.clicked.connect(self.clear_unfinished_list)
            unfinished_dialog.exec_()
        except TypeError:
            pass

    def clear_unfinished_list(self):
        self.unfinished_downloads.clear()
        self.unfinished_downloads_available = False

    def reset_unfinished_downloads(self):
        self.unfinished_downloads_available = False

    def display_imgur_client_information(self):
        """Opens a dialog that tells the user how many imgur credits they have remaining"""
        if self.imgur_client[0] is not None and self.imgur_client[1] is not None:
            try:
                imgur_client = imgurpython.ImgurClient(self.imgur_client[0], self.imgur_client[1])
            except imgurpython.helpers.error.ImgurClientError:
                imgur_client = None
                Message.invalid_imgur_client(self)
        else:
            Message.no_imgur_client(self)
            imgur_client = None

        if imgur_client is not None:
            credits_dict = imgur_client.credits
            dialog_text = 'Application credit limit: %s\nApplication credits remaining: %s\n\nUser credit limit: %s' \
                          '\nUser credits remaining: %s\nTime user credits reset: %s' %\
                          (credits_dict['ClientLimit'], credits_dict['ClientRemaining'], credits_dict['UserLimit'],
                           credits_dict['UserRemaining'],
                           date.strftime(datetime.fromtimestamp(credits_dict['UserReset']), '%m-%d-%Y at %I:%M %p'))
            reply = QtWidgets.QMessageBox.information(self, 'Imgur Credits', dialog_text, QtWidgets.QMessageBox.Ok)

    def display_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def open_user_manual(self):
        """Opens the user manual using the default PDF viewer"""
        manual = 'The Downloader For Reddit - User Manual.pdf'
        if os.path.isfile(os.path.join(os.getcwd(), manual)):
            file = os.path.join(os.getcwd(), manual)
        else:
            separator = '/' if not sys.platform == 'win32' else '\\'
            containing_folder, current = os.getcwd().rsplit(separator, 1)
            file = os.path.join(containing_folder, manual)
        try:
            if sys.platform == 'win32':
                os.startfile(file)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, file])
        except FileNotFoundError:
            Message.user_manual_not_found(self)

    def refresh_user_count(self):
        """Updates the shown user count seen in the list menu"""
        try:
            self.user_count = len(self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list)
        except:
            self.user_count = 0
        self.file_user_list_count.setText('User List Count: %s' % self.user_count)

    def refresh_subreddit_count(self):
        """Updates the shown subreddit count seen in the list menu"""
        try:
            self.subreddit_count = len(self.subreddit_view_chooser_dict[
                                           self.subreddit_list_combo.currentText()].reddit_object_list)
        except:
            self.subreddit_count = 0
        self.file_subreddit_list_count.setText('Subreddit List Count: %s' % self.subreddit_count)

    def set_list_sort_method(self, method):
        self.list_sort_method = method
        self.change_list_sort_method()

    def set_list_order_method(self, method):
        self.list_order_method = method
        self.change_list_sort_method()

    def change_list_sort_method(self):
        """Applies the sort and order function to each list model"""
        for key, value in self.user_view_chooser_dict.items():
            value.sort_lists((self.list_sort_method, self.list_order_method))
        for key, value in self.subreddit_view_chooser_dict.items():
            value.sort_lists((self.list_sort_method, self.list_order_method))

    def set_view_menu_items_checked(self):
        """A dispatch table to set the correct view menu item checked"""
        view_sort_dict = {0: self.view_sort_list_by_name,
                          1: self.view_sort_list_by_date_added,
                          2: self.view_sort_list_by_number_of_downloads}
        view_order_dict = {0: self.view_order_by_ascending,
                           1: self.view_order_by_descending}
        view_sort_dict[self.list_sort_method].setChecked(True)
        view_order_dict[self.list_order_method].setChecked(True)

    def closeEvent(self, QCloseEvent):
        if self.unfinished_downloads_available:
            unfinished_dialog = UnfinishedDownloadsWarning()
            dialog = unfinished_dialog.exec_()
            if dialog == QtWidgets.QMessageBox.Accepted:
                self.close()
            else:
                QCloseEvent.ignore()
        else:
            self.close()

    def close(self):
        self.receiver.stop_run()
        self.save_main_window_settings()
        if self.settings_manager.auto_save:
            self.save_state()

    def save_main_window_settings(self):
        self.settings_manager.main_window_geom = self.saveGeometry()
        self.settings_manager.list_sort_method = self.list_sort_method
        self.settings_manager.list_order_method = self.list_order_method
        self.settings_manager.download_users = self.download_users_checkbox.isChecked()
        self.settings_manager.download_subreddits = self.download_subreddit_checkbox.isChecked()
        self.settings_manager.save_main_window()

    def load_state(self):
        """Gets the loaded items from the settings manager and supplies the information to the GUI and List Models"""
        reddit_object_lists = self.settings_manager.load_pickeled_state()
        last_user_view = reddit_object_lists[2]
        last_subreddit_view = reddit_object_lists[3]
        try:
            self.user_view_chooser_dict = reddit_object_lists[0]
            self.subreddit_view_chooser_dict = reddit_object_lists[1]
            for name, item in self.user_view_chooser_dict.items():
                self.user_lists_combo.addItem(name)
            for name, item in self.subreddit_view_chooser_dict.items():
                self.subreddit_list_combo.addItem(name)
            self.user_lists_combo.setCurrentText(last_user_view)
            self.subreddit_list_combo.setCurrentText(last_subreddit_view)
            self.user_list_view.setModel(self.user_view_chooser_dict[last_user_view])
            self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[last_subreddit_view])
        except KeyError:
            pass

    def save_state(self):
        """Pickles the user and subreddit lists and saves any settings that need to be saved"""
        self.settings_manager.save_all()
        user_list_models = {}
        subreddit_list_models = {}
        current_user_view = self.user_lists_combo.currentText()
        current_subreddit_view = self.subreddit_list_combo.currentText()

        for key, value in self.user_view_chooser_dict.items():
            name = value.name
            object_list = value.reddit_object_list
            user_list_models[name] = object_list

        for key, value in self.subreddit_view_chooser_dict.items():
            name = value.name
            object_list = value.reddit_object_list
            subreddit_list_models[name] = object_list
        # TODO: Find someway to show that this has been saved on the GUI
        if not self.settings_manager.save_pickle_state(user_list_models, subreddit_list_models, current_user_view,
                                                       current_subreddit_view):
            Message.failed_to_save(self)

    def check_for_updates(self, from_menu):
        """
        Opens and runs the update checker on a separate thread. Sets self.from_menu so that other dialogs know the
        updater has been ran by the user, this will result in different dialog behaviour
        """
        self.update_thread = QtCore.QThread()
        self.update_checker = UpdateChecker(self.version)
        self.update_checker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_checker.run)
        self.update_checker.update_available_signal.connect(self.display_update)
        if from_menu:
            self.update_checker.no_update_signal.connect(self.no_update_available_dialog)
        self.update_checker.finished.connect(self.update_thread.quit)
        self.update_checker.finished.connect(self.update_checker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_thread.start()

    def display_update(self, latest_version):
        if self.settings_manager.do_not_notify_update != latest_version:
            self.update_dialog(latest_version)

    def update_dialog(self, update_variables):
        """Opens the update dialog"""
        update_checker = UpdateDialog(update_variables)
        update_checker.show()
        dialog = update_checker.exec_()

    def no_update_available_dialog(self):
        Message.up_to_date_message(self)

    def check_first_run(self):
        if self.settings_manager.check_first_run():
            if self.check_reddit_objects():
                if Message.update_reddit_objects_message(self):
                    self.update_reddit_objects()

    def check_reddit_objects(self):
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                try:
                    if user.version != self.version:
                        return True
                except AttributeError:
                    return True

    def update_reddit_objects(self):
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                try:
                    if user.version != self.version:
                        self.update_object_version(value.reddit_object_list, user)
                except AttributeError:
                    self.update_object_version(value.reddit_object_list, user)

    def update_object_version(self, object_list, reddit_object):
        x = User(self.version, reddit_object.name, reddit_object.save_path, reddit_object.post_limit,
                 reddit_object.avoid_duplicates, reddit_object.download_videos, reddit_object.download_images,
                 reddit_object.save_subreddits_by, reddit_object.name_downloads_by, reddit_object.user_added)
        x.do_not_edit = reddit_object.do_not_edit
        x.saved_submissions = reddit_object.saved_submissions
        x.already_downloaded = reddit_object.already_downloaded
        x.date_limit = reddit_object.date_limit
        x.custom_date_limit = reddit_object.custom_date_limit
        x.saved_content = reddit_object.saved_content
        x.number_of_downloads = reddit_object.number_of_downloads
        object_list.remove(reddit_object)
        object_list.append(x)
