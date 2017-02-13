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
import subprocess
import shelve
from datetime import datetime
import imgurpython
from PyQt5 import QtWidgets, QtCore, QtGui

from RD_GUI_auto import Ui_MainWindow
from RedditObjects import User, Subreddit
from ListModel import ListModel
from RedditExtractor import RedditExtractor
from AddUserDialog import AddUserDialog
from settingsGUI import RedditDownloaderSettingsGUI
from UserSettingsDialog import UserSettingsDialog
from SubredditSettingsDialog import SubredditSettingsDialog
from Messages import Message, UnfinishedDownloadsWarning, UpdateDialog
from FailedDownloadsDialog import FailedDownloadsDialog
from UserFinderGUI import UserFinderGUI
from UnfinishedDownloadsDialog import UnfinishedDownloadsDialog
from AboutDialog import AboutDialog
from UpdaterChecker import UpdateChecker
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
        self.last_downloaded_users = []
        self.download_count = 0
        self.running = False
        self.user_finder_open = False

        self.settings = QtCore.QSettings('SomeGuySoftware', 'RedditDownloader')

        self.last_update = self.settings.value('last_update', None, type=str)
        # self.last_update = None

        self.total_files_downloaded = self.settings.value('total_files_downloaded', 0, type=int)
        self.restoreGeometry(self.settings.value('window_geometry', self.saveGeometry()))
        self.download_users_checkbox.setCheckState(self.settings.value('download_users_checkbox', 0, type=int))
        self.download_subreddit_checkbox.setCheckState(self.settings.value('download_subreddit_checkbox', 0, type=int))
        self.run_user_finder_auto = self.settings.value('run_user_finder_auto', False, type=bool)

        self.unfinished_downloads_available = False
        self.unfinished_downloads = None

        # Settings supplied to other parts of the program
        self.imgur_client = self.settings.value('imgur_client', (None, None), type=tuple)
        self.reddit_username = self.settings.value('reddit_username', None, type=str)
        self.reddit_password = self.settings.value('reddit_password', None, type=str)
        self.auto_save_on_close = self.settings.value('auto_save_on_close', False, type=bool)

        self.restrict_date = self.settings.value('restrict_date', False, type=bool)
        self.post_limit = self.settings.value('post_limit', 25, type=int)
        self.download_videos = self.settings.value('download_video', True, type=bool)
        self.download_images = self.settings.value('download_images', True, type=bool)
        self.avoid_duplicates = self.settings.value('avoid_duplicates', True, type=bool)

        self.restrict_by_submission_score = self.settings.value('restrict_by_submission_score', False, type=bool)
        self.restrict_by_submission_score_method = self.settings.value('restrict_by_submission_score_method', 0,
                                                                       type=int)
        self.restrict_by_submission_score_limit = self.settings.value('restrict_by_submission_score_limit', 3000,
                                                                      type=int)

        self.subreddit_sort_method = self.settings.value('subreddit_sort_method', 0, type=int)
        self.subreddit_sort_top_method = self.settings.value('subreddit_sort_top_method', 0, type=int)

        self.save_subreddits_by = self.settings.value('save_subreddits_by', 'Subreddit Name', type=str)
        self.name_downloads_by = self.settings.value('name_downloads_by', 'Image/Album Id', type=str)
        self.save_path = self.settings.value('save_path', "%s%s" % (os.path.expanduser('~'), '/Downloads/'), type=str)

        self.restrict_by_custom_date = self.settings.value('restrict_by_custom_date', False, type=bool)
        self.custom_date = self.settings.value('custom__date', 0, type=int)

        self.list_sort_method = (self.settings.value('list_sort_method', (0, 0), type=tuple))
        # End of settings

        self.queue = queue
        self.receiver = receiver
        self.user_view_chooser_dict = {}
        self.subreddit_view_chooser_dict = {}
        self.load_state()

        self.auto_display_failed_list = self.settings.value('auto_display_failed_list', True, type=bool)

        self.file_add_user_list.triggered.connect(self.add_user_list)
        self.file_remove_user_list.triggered.connect(self.remove_user_list)
        self.file_add_subreddit_list.triggered.connect(self.add_subreddit_list)
        self.file_remove_subreddit_list.triggered.connect(self.remove_subreddit_list)
        self.file_failed_download_list.triggered.connect(self.display_failed_downloads)
        self.file_last_downloaded_users.triggered.connect(self.open_last_downloaded_users)
        self.file_unfinished_downloads.triggered.connect(self.display_unfinished_downloads_dialog)
        self.file_imgur_credits.triggered.connect(self.display_imgur_client_information)
        self.file_user_manual.triggered.connect(self.open_user_manual)
        self.file_check_for_updates.triggered.connect(self.check_for_updates)
        self.file_about.triggered.connect(self.display_about_dialog)
        self.file_user_list_count.triggered.connect(lambda: self.user_settings(0, True))
        self.file_subreddit_list_count.triggered.connect(lambda: self.subreddit_settings(0, True))

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
        self.progress_bar.setToolTip('Displays the progress of user/subreddit validation, then link extraction')
        self.progress_bar.setVisible(False)
        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setText('Extraction Complete')

        self.check_for_updates(False)

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
        try:
            if not from_menu:
                position = self.get_selected_view_index(self.user_list_view).row()
            else:
                position = 0
            user_settings_dialog = UserSettingsDialog(current_list_model,
                                                      current_list_model.reddit_object_list[position], False)
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
        except AttributeError:
            Message.no_user_selected(self)

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
        self.reddit_extractor = RedditExtractor(user_list, None, self.queue, self.post_limit,
                                                self.save_path, self.subreddit_sort_method,
                                                self.subreddit_sort_top_method, self.restrict_date,
                                                self.restrict_by_submission_score,
                                                self.restrict_by_submission_score_method,
                                                self.restrict_by_submission_score_limit, None)
        self.start_reddit_extractor_thread('user')

    def run_single_user(self, user):
        """
        Called from the user settings dialog and supplied the name of the selected user.  Downloads only the
        selected user
        """
        self.started_download_gui_shift()
        user_list = [user]
        self.reddit_extractor = RedditExtractor(user_list, None, self.queue, self.post_limit,
                                                self.save_path, self.subreddit_sort_method,
                                                self.subreddit_sort_top_method, self.restrict_date,
                                                self.restrict_by_submission_score,
                                                self.restrict_by_submission_score_method,
                                                self.restrict_by_submission_score_limit, None)
        self.start_reddit_extractor_thread('user')

    def run_subreddit(self):
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.reddit_extractor = RedditExtractor(None, subreddit_list, self.queue, self.post_limit,
                                                self.save_path, self.subreddit_sort_method,
                                                self.subreddit_sort_top_method, self.restrict_date,
                                                self.restrict_by_submission_score,
                                                self.restrict_by_submission_score_method,
                                                self.restrict_by_submission_score_limit, None)
        self.start_reddit_extractor_thread('subreddit')

    def run_single_subreddit(self, subreddit):
        """
        Called from the subreddit settings dialog and supplied the name of the selected subreddit.  Downloads only the
        selected subreddit
        """
        self.started_download_gui_shift()
        subreddit_list = [subreddit]
        self.reddit_extractor = RedditExtractor(None, subreddit_list, self.queue, self.post_limit,
                                                self.save_path, self.subreddit_sort_method,
                                                self.subreddit_sort_top_method, self.restrict_date,
                                                self.restrict_by_submission_score,
                                                self.restrict_by_submission_score_method,
                                                self.restrict_by_submission_score_limit, None)
        self.start_reddit_extractor_thread('subreddit')

    def run_user_and_subreddit(self):
        """
        Downloads from the users in the user list only the content which has been posted to the subreddits in the
        subreddit list.
        """
        user_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.reddit_extractor = RedditExtractor(user_list, subreddit_list, self.queue, self.post_limit,
                                                self.save_path, self.subreddit_sort_method,
                                                self.subreddit_sort_top_method, self.restrict_date,
                                                self.restrict_by_submission_score,
                                                self.restrict_by_submission_score_method,
                                                self.restrict_by_submission_score_limit, None)
        self.start_reddit_extractor_thread('users_and_subreddits')

    def run_unfinished_downloads(self):
        """Downloads the content that was left during the last run if the user clicked the stop download button"""
        self.download_count = 0
        self.started_download_gui_shift()
        self.reddit_extractor = RedditExtractor(None, None, self.queue, None, None, None, None, None,
                                                None, None, None,  self.unfinished_downloads)
        self.start_reddit_extractor_thread('unfinished')

    def start_reddit_extractor_thread(self, download_type):
        """Moves the extractor to a different thread and calls the appropriate function for the type of download"""
        self.stop_download.connect(self.reddit_extractor.stop_download)
        self.thread = QtCore.QThread()
        self.reddit_extractor.moveToThread(self.thread)
        if download_type == 'user':
            self.thread.started.connect(self.reddit_extractor.validate_users)
        elif download_type == 'subreddit':
            self.thread.started.connect(self.reddit_extractor.validate_subreddits)
        elif download_type == 'users_and_subreddits':
            self.thread.started.connect(self.reddit_extractor.validate_users_and_subreddits)
        elif download_type == 'unfinished':
            self.thread.started.connect(self.reddit_extractor.finish_downloads)
        self.reddit_extractor.remove_invalid_user.connect(self.remove_invalid_user)
        self.reddit_extractor.downloaded_users_signal.connect(self.fill_downloaded_users_list)
        self.reddit_extractor.status_bar_update.connect(self.update_status_bar)
        self.reddit_extractor.setup_progress_bar.connect(self.setup_progress_bar)
        self.reddit_extractor.update_progress_bar.connect(self.update_progress_bar)
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
        if not self.user_finder_open:
            if text.lower().startswith('failed'):
                self.failed_list.append(text)
            elif text.startswith('Saved'):
                self.update_status_bar_download_count()
        self.output_box.append(text)
        if self.user_finder_open and text.startswith('Saved') or text.lower().startswith('failed'):
            self.update_user_finder_progress_bar()

    def update_status_bar(self, text):
        self.statusbar.showMessage(text, -1)
        if text.startswith('Downloaded'):
            x, self.soft_downloaded = text.rsplit(' ', 1)

    def update_status_bar_download_count(self):
        self.download_count += 1
        self.total_files_downloaded += 1
        self.statusbar.showMessage('Downloaded: %s  of  %s' % (self.download_count, self.soft_downloaded), -1)

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
        if self.progress_bar.value() == self.progress_bar.maximum() and self.bar_count == 1:
            self.progress_bar.setVisible(False)
            self.statusbar.addPermanentWidget(self.progress_label)
        elif self.progress_bar.value() == self.progress_bar.maximum() and self.bar_count == 0:
            self.bar_count += 1

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
                    self.user_view_chooser_dict[self.user_lists_combo.currentText()].sort_lists(self.list_sort_method)
                else:
                    self.user_list_view.setModel(None)
                self.refresh_user_count()
        except KeyError:
            Message.no_user_list(self)

    def change_user_list(self):
        """Changes the user list model based on the user_list_combo"""
        new_list_view = self.user_lists_combo.currentText()
        self.user_list_view.setModel(self.user_view_chooser_dict[new_list_view])
        self.user_view_chooser_dict[new_list_view].sort_lists(self.list_sort_method)
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
                        self.subreddit_lists_combo.currentText()].sort_lists(self.list_sort_method)
                else:
                    self.subreddit_list_view.setModel(None)
                self.refresh_subreddit_count()
        except KeyError:
            Message.no_subreddit_list(self)

    def change_subreddit_list(self):
        new_list_view = self.subreddit_list_combo.currentText()
        self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[new_list_view])
        self.subreddit_view_chooser_dict[new_list_view].sort_lists(self.list_sort_method)
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
            x = User(new_user, self.save_path, self.imgur_client, self.post_limit, self.name_downloads_by,
                     self.avoid_duplicates, self.download_videos, self.download_images, datetime.now().timestamp())
            insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
            insertion_list.setData(insertion_list.rowCount() - 1, x)
        insertion_list.sort_lists(self.list_sort_method)
        self.refresh_user_count()

    def add_user(self, new_user):
        """Adds a user to the current list"""
        insertion_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        try:
            if new_user != '' and ' ' not in new_user:
                if any(new_user.lower() == name.lower() for name in insertion_list.display_list):
                    Message.name_in_list(self)
                else:
                    x = User(new_user, self.save_path, self.imgur_client, self.post_limit, self.name_downloads_by,
                             self.avoid_duplicates, self.download_videos, self.download_images,
                             datetime.now().timestamp())
                    insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
                    insertion_list.setData(insertion_list.rowCount() - 1, x)
                    insertion_list.sort_lists(self.list_sort_method)
                    self.refresh_user_count()
            else:
                Message.not_valid_name(self)

        except KeyError:
            Message.no_user_list(self)

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
                    x = Subreddit(new_sub, self.save_path, self.post_limit, self.save_subreddits_by, self.imgur_client,
                                  self.name_downloads_by, self.avoid_duplicates, self.download_videos,
                                  self.download_images, datetime.now().timestamp())
                    insertion_list.insertRows(insertion_list.rowCount() + 1, 1)
                    insertion_list.setData(insertion_list.rowCount() - 1, x)
                    insertion_list.sort_lists(self.list_sort_method)
                    self.refresh_subreddit_count()
            else:
                Message.not_valid_name(self)
        except KeyError:
            Message.no_subreddit_list(self)

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

    def fill_downloaded_users_list(self, users):
        """Adds a users name to a list if they had content downloaded while the program is open"""
        for user in self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list:
            if user.name in users:
                self.last_downloaded_users.append(user)
        self.file_last_downloaded_users.setEnabled(True)

    def open_last_downloaded_users(self):
        """
        Opens a dialog that shows the downloads of any user that has been added to the last downloaded users list.
        The dialog that is opened is the user settings dialog with certain restrictions implemented and buttons set to
        not visible.
        """
        if len(self.last_downloaded_users) > 0:
            users_dialog = UserSettingsDialog(self.last_downloaded_users, self.last_downloaded_users[0], True)
            users_dialog.change_to_downloads_view()
            users_dialog.view_downloads_button.setText('Show Downloads')
            # users_dialog.view_downloads_button.setVisible(False)
            users_dialog.restore_defaults_button.setVisible(False)
            users_dialog.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
            users_dialog.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')
            users_dialog.exec_()
        else:
            Message.no_users_downloaded(self)

    def started_download_gui_shift(self):
        """Disables certain options in the GUI that may be problematic if used while the downloader is running"""
        self.running = True
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
        self.progress_label.setText('Download complete')
        if self.auto_display_failed_list and len(self.failed_list) > 0:
            self.display_failed_downloads()
        self.download_count = 0

    def open_settings_dialog(self):
        """Displays the main settings dialog"""
        settings = RedditDownloaderSettingsGUI()
        settings.total_files_downloaded_label.setText('Total Files Downloaded: %s' % self.total_files_downloaded)
        dialog = settings.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.reddit_username = settings.reddit_account_username
            self.reddit_password = settings.reddit_account_password
            self.auto_save_on_close = settings.auto_save_checkbox.isChecked()
            if settings.date_restriction_checkbox.isChecked() or settings.restrict_by_custom_date_checkbox.isChecked():
                self.restrict_date = True
            else:
                self.restrict_date = False
            self.download_videos = settings.link_filter_video_checkbox.isChecked()
            if settings.link_filter_avoid_duplicates_checkbox.isChecked() != self.avoid_duplicates:
                self.change_avoid_duplicates(settings.link_filter_avoid_duplicates_checkbox.isChecked())
            self.subreddit_sort_method = settings.subreddit_sort_method
            self.subreddit_sort_top_method = settings.sub_sort_top_method

            if settings.restrict_to_score_checkbox.isChecked():
                self.restrict_by_submission_score = True
                self.restrict_by_submission_score_method = settings.post_score_method
                self.restrict_by_submission_score_limit = settings.post_score_limit_spin_box.value()
            else:
                self.restrict_by_submission_score = False
                self.restrict_by_submission_score_limit = 1

            self.subreddit_sort_top_method = settings.sub_sort_top_method
            self.change_post_limit(settings.set_post_limit)
            if settings.subreddit_save_by_combo.currentText() != self.save_subreddits_by:
                self.change_save_subreddits_by(settings.subreddit_save_by_combo.currentText())
            if settings.name_downloads_by_combo.currentText() != self.name_downloads_by:
                self.change_name_downloads_by(settings.name_downloads_by_combo.currentText())

            if settings.save_directory_line_edit.text() != self.save_path:
                self.change_save_path(settings.save_directory_line_edit.text())

            imgur_client = (settings.imgur_client_id, settings.imgur_client_secret)
            if imgur_client != self.imgur_client:
                self.change_imgur_client(imgur_client)

            if settings.custom_date != self.custom_date:
                self.custom_date = settings.custom_date
                self.change_custom_date()

            if settings.list_sort_method != self.list_sort_method:
                self.list_sort_method = settings.list_sort_method
                self.change_list_sort_method()

            self.save_state()

    """
    The following functions change options set in the settings menu that must be provided to each list model object.
    These functions go through each object in every list and update the individual options
    """
    def change_post_limit(self, new_limit):
        self.post_limit = new_limit
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_post_limit(new_limit)
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_post_limit(new_limit)

    def change_save_subreddits_by(self, new_method):
        self.save_subreddits_by = new_method
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_subreddit_save_by_method(new_method)

    def change_save_path(self, new_save_path):
        self.save_path = new_save_path
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_save_path(new_save_path)
        method = None if self.save_subreddits_by != 'Subreddit Name' else 'Subreddit Name'
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_save_path(new_save_path)
                sub.update_subreddit_save_by_method(method)

    def change_imgur_client(self, new_client):
        self.imgur_client = new_client
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_imgur_client(new_client)
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_imgur_client(new_client)

    def change_name_downloads_by(self, new_method):
        self.name_downloads_by = new_method
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_name_downloads_by(new_method)
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_name_downloads_by(new_method)

    def change_avoid_duplicates(self, state):
        self.avoid_duplicates = state
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_avoid_duplicates(state)
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_avoid_duplicates(state)

    def change_custom_date(self):
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_custom_date_limit(self.custom_date)
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_custom_date_limit(self.custom_date)

    def change_list_sort_method(self):
        for key, value in self.user_view_chooser_dict.items():
            value.sort_lists(self.list_sort_method)
        for key, value in self.subreddit_view_chooser_dict.items():
            value.sort_lists(self.list_sort_method)

    def update_number_of_downloads(self):
        for key, value in self.user_view_chooser_dict.items():
            for user in value.reddit_object_list:
                user.update_number_of_downloads()
        for key, value in self.subreddit_view_chooser_dict.items():
            for sub in value.reddit_object_list:
                sub.update_number_of_downloads()

    def display_failed_downloads(self):
        """Opens a dialog with information about any content that was not able to be downloaded for whatever reason"""
        failed_dialog = FailedDownloadsDialog(self.failed_list)
        failed_dialog.auto_display_checkbox.setChecked(not self.auto_display_failed_list)
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
        """Opens a dialog that tells the user how many imgur creadits they have remaining"""
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
            dialog_text = 'Imgur credit limit: %s\n\nImgur credits remaining: %s' % (credits_dict['ClientLimit'],
                                                                                     credits_dict['ClientRemaining'])
            reply = QtWidgets.QMessageBox.information(self, 'Imgur Credits', dialog_text, QtWidgets.QMessageBox.Ok)

    def display_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec_()

    def open_user_manual(self):
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
        """Updates the shown user count seen in the file menu"""
        try:
            self.user_count = len(self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list)
        except:
            self.user_count = 0
        self.file_user_list_count.setText('User List Count: %s' % self.user_count)

    def refresh_subreddit_count(self):
        try:
            self.subreddit_count = len(self.subreddit_view_chooser_dict[
                                           self.subreddit_list_combo.currentText()].reddit_object_list)
        except:
            self.subreddit_count = 0
        self.file_subreddit_list_count.setText('Subreddit List Count: %s' % self.subreddit_count)

    def closeEvent(self, QCloseEvent):
        if self.unfinished_downloads_available:
            unfinished_dialog = UnfinishedDownloadsWarning()
            dialog = unfinished_dialog.exec_()
            if dialog == QtWidgets.QMessageBox.Accepted:
                self.receiver.stop_run()
                self.settings.setValue('window_geometry', self.saveGeometry())
                self.settings.setValue('total_files_downloaded', self.total_files_downloaded)
                self.settings.setValue('last_update', self.last_update)
                if self.auto_save_on_close:
                    self.save_state()
            else:
                QCloseEvent.ignore()
        else:
            self.receiver.stop_run()
            self.settings.setValue('window_geometry', self.saveGeometry())
            self.settings.setValue('total_files_downloaded', self.total_files_downloaded)
            self.settings.setValue('last_update', self.last_update)
            if self.auto_save_on_close:
                self.save_state()

    def load_state(self):
        with shelve.open('save_file', 'c') as shelf:
            try:
                user_list_models = shelf['user_list_models']
                subreddit_list_models = shelf['subreddit_list_models']
                last_user_view = shelf['current_user_view']
                last_subreddit_view = shelf['current_subreddit_view']

                for name, user_list in user_list_models.items():
                    x = ListModel(name, 'user')
                    x.reddit_object_list = user_list
                    x.display_list = [i.name for i in user_list]
                    self.user_view_chooser_dict[x.name] = x
                    self.user_lists_combo.addItem(x.name)

                for name, subreddit_list in subreddit_list_models.items():
                    x = ListModel(name, 'subreddit')
                    x.reddit_object_list = subreddit_list
                    x.display_list = [i.name for i in subreddit_list]
                    self.subreddit_view_chooser_dict[x.name] = x
                    self.subreddit_list_combo.addItem(x.name)

                self.user_lists_combo.setCurrentText(last_user_view)
                self.subreddit_list_combo.setCurrentText(last_subreddit_view)

                self.user_list_view.setModel(self.user_view_chooser_dict[last_user_view])
                self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[last_subreddit_view])

            except KeyError:
                pass

    def save_state(self):
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
        try:
            with shelve.open('save_file', 'c') as shelf:
                shelf['user_list_models'] = user_list_models
                shelf['subreddit_list_models'] = subreddit_list_models
                shelf['current_user_view'] = current_user_view
                shelf['current_subreddit_view'] = current_subreddit_view
        except:
            Message.failed_to_save(self)

        self.settings.setValue('imgur_client', self.imgur_client)
        self.settings.setValue('reddit_username', self.reddit_username)
        self.settings.setValue('reddit_password', self.reddit_password)
        self.settings.setValue('auto_save_on_close', self.auto_save_on_close)
        self.settings.setValue('run_user_finder_auto', self.run_user_finder_auto)

        self.settings.setValue('restrict_date', self.restrict_date)
        self.settings.setValue('post_limit', self.post_limit)
        self.settings.setValue('download_videos', self.download_videos)
        self.settings.setValue('download_images', self.download_images)
        self.settings.setValue('avoid_duplicates', self.avoid_duplicates)

        self.settings.setValue('restrict_by_submission_score', self.restrict_by_submission_score)
        self.settings.setValue('restrict_by_submission_score_method', self.restrict_by_submission_score_method)
        self.settings.setValue('restrict_by_submission_score_limit', self.restrict_by_submission_score_limit)

        self.settings.setValue('subreddit_sort_method', self.subreddit_sort_method)
        self.settings.setValue('subreddit_sort_top_method', self.subreddit_sort_top_method)

        self.settings.setValue('save_subreddits_by', self.save_subreddits_by)
        self.settings.setValue('name_downloads_by', self.name_downloads_by)
        self.settings.setValue('save_path', self.save_path)

        self.settings.setValue('auto_display_failed_list', self.auto_display_failed_list)

        self.settings.setValue('download_users_checkbox', self.download_users_checkbox.checkState())
        self.settings.setValue('download_subreddit_checkbox', self.download_subreddit_checkbox.checkState())

        self.settings.setValue('restrict_by_custom_date', self.restrict_by_custom_date)
        self.settings.setValue('custom__date', self.custom_date)

        self.settings.setValue('list_sort_method', self.list_sort_method)

    def check_for_updates(self, from_menu):
        self.update_thread = QtCore.QThread()
        self.update_checker = UpdateChecker(self.version)
        self.update_checker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_checker.run)
        self.update_checker.update_available_signal.connect(self.update_dialog)
        if from_menu:
            self.update_checker.no_update_signal.connect(self.no_update_available_dialog)
        self.update_checker.finished.connect(self.update_thread.quit)
        self.update_checker.finished.connect(self.update_checker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_thread.start()

    def update_dialog(self, update_variables):
        if self.last_update != update_variables[0]:
            update_checker = UpdateDialog(update_variables)
            update_checker.show()
            dialog = update_checker.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                self.run_updater()
            else:
                self.last_update = update_checker.set_last_update

    def no_update_available_dialog(self):
        Message.up_to_date_message(self)

    def run_updater(self):
        platform = sys.platform
        split_char = '\\' if platform == 'win32' else '/'
        updater = '%s%s%sdfr_updater%s' % (os.getcwd(), split_char, 'dfr_updater/', '.exe' if platform == 'win32' else '')
        updater = ''.join([x if x != '\\' else '/' for x in updater])
        try:
            if platform == 'win32':
                os.startfile(updater)
            else:
                subprocess.Popen([updater, updater])
        except:
            self.update_output(updater)
