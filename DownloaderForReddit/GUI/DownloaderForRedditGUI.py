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
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import logging

from ..GUI_Resources.DownloaderForRedditGUI_auto import Ui_MainWindow
from ..GUI.AboutDialog import AboutDialog
from ..GUI.DownloadedObjectsDialog import DownloadedObjectsDialog
from ..GUI.FailedDownloadsDialog import FailedDownloadsDialog
from ..Core.Messages import Message, UnfinishedDownloadsWarning
from ..GUI.RedditObjectSettingsDialog import RedditObjectSettingsDialog
from ..Core.DownloadRunner import DownloadRunner
from ..Core.RedditObjects import User, Subreddit
from ..GUI.UnfinishedDownloadsDialog import UnfinishedDownloadsDialog
from ..GUI.UpdateDialogGUI import UpdateDialog
from ..Core.UpdaterChecker import UpdateChecker
from ..GUI.DownloaderForRedditSettingsGUI import RedditDownloaderSettingsGUI
from ..Utils import Injector, SystemUtil, ImgurUtils
from ..Persistence.ObjectStateHandler import ObjectStateHandler
from ..ViewModels.ListModel import ListModel
from ..GUI.AddRedditObjectDialog import AddUserDialog
from ..version import __version__


class DownloaderForRedditGUI(QtWidgets.QMainWindow, Ui_MainWindow):

    stop_download = QtCore.pyqtSignal()
    update_user_finder = QtCore.pyqtSignal()

    def __init__(self, queue, receiver):
        """
        The main GUI window that all interaction is done through.

        :param queue: An instance of the queue initialized in the "main" function and passed to the main GUI window in
         order to update the main GUI output box.
        :param receiver: The receiver that is initialized in the "main" function and moved to another thread.  This
        keeps the queue updated with fresh output from all throughout the program.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.version = __version__
        self.failed_list = []
        self.last_downloaded_objects = {}
        self.download_count = 0
        self.downloaded = 0
        self.running = False
        self.saved = True
        self.user_finder = None

        # region Settings
        self.settings_manager = Injector.get_settings_manager()

        geom = self.settings_manager.main_window_geom
        horz_splitter_state = self.settings_manager.horz_splitter_state
        vert_splitter_state = self.settings_manager.vert_splitter_state
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())
        self.horz_splitter.restoreState(horz_splitter_state if horz_splitter_state is not None else
                                        self.horz_splitter.saveState())
        self.vert_splitter.restoreState(vert_splitter_state if vert_splitter_state is not None else
                                        self.vert_splitter.saveState())
        self.list_sort_method = self.settings_manager.list_sort_method
        self.list_order_method = self.settings_manager.list_order_method
        self.download_users_checkbox.setChecked(self.settings_manager.download_users)
        self.download_subreddit_checkbox.setChecked(self.settings_manager.download_subreddits)
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
        self.file_last_downloaded_list.triggered.connect(self.open_last_downloaded_list)
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
        if len(self.last_downloaded_objects) < 1:
            self.file_last_downloaded_list.setEnabled(False)
        if len(self.failed_list) < 1:
            self.file_failed_download_list.setEnabled(False)

        # self.file_open_user_finder.triggered.connect(lambda: self.display_user_finder(False))
        self.file_open_user_finder.setEnabled(False)
        self.menuUser_Finder.setToolTip('The user finder has been disabled for this version, but will be included '
                                        'in a future release')

        self.file_open_settings.triggered.connect(self.open_settings_dialog)
        self.file_save.triggered.connect(self.save_state)
        self.file_import_save_file.triggered.connect(self.import_save_file)
        self.file_open_save_file_location.triggered.connect(self.open_save_file_location)
        self.file_exit.triggered.connect(self.close_from_menu)

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

        self.progress_bar = QtWidgets.QProgressBar()
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.bar_count = 0
        self.progress_bar.setToolTip('Displays the progress of user/subreddit validation and link extraction')
        self.progress_bar.setVisible(False)
        self.progress_label = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(self.progress_label)
        self.progress_label.setText('Extraction Complete')
        self.progress_label.setVisible(False)

        # self.check_for_updates(False)

    def set_saved(self):
        self.saved = True
        self.setWindowTitle("Downloader For Reddit")

    def set_not_saved(self):
        self.saved = False
        self.setWindowTitle("Downloader For Reddit *")

    def user_list_right_click(self):
        user_menu = QtWidgets.QMenu()
        try:
            position = self.get_selected_view_index(self.user_list_view).row()
            user = self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list[position]
            valid = True
        except AttributeError:
            user = None
            valid = False

        user_settings = user_menu.addAction("User Settings")
        user_downloads = user_menu.addAction("View User Downloads")
        user_menu.addSeparator()
        open_user_folder = user_menu.addAction("Open Download Folder")
        user_menu.addSeparator()
        add_user = user_menu.addAction("Add User")
        remove_user = user_menu.addAction("Remove User")

        if user is not None:
            user_menu.addSeparator()
            download_enabled_text = 'Enable Download' if not user.enable_download else 'Disable Download'
            toggle_download_enabled = user_menu.addAction(download_enabled_text)
            toggle_download_enabled.triggered.connect(lambda: user.toggle_enable_download())

        add_user.triggered.connect(self.add_user_dialog)
        remove_user.triggered.connect(self.remove_user)
        user_settings.triggered.connect(lambda: self.user_settings(0, False))
        user_downloads.triggered.connect(lambda: self.user_settings(1, False))
        open_user_folder.triggered.connect(self.open_user_download_folder)

        if not valid:
            user_settings.setVisible(False)
            user_downloads.setVisible(False)
            open_user_folder.setVisible(False)
            remove_user.setVisible(False)

        if self.running:
            add_user.setEnabled(False)
            remove_user.setEnabled(False)

        user_menu.exec(QtGui.QCursor.pos())

    def subreddit_list_right_click(self):
        subreddit_menu = QtWidgets.QMenu()
        try:
            position = self.get_selected_view_index(self.subreddit_list_view).row()
            subreddit = self.subreddit_view_chooser_dict[
                self.subreddit_list_combo.currentText()].reddit_object_list[position]
            valid = True
        except AttributeError:
            subreddit = None
            valid = False

        subreddit_settings = subreddit_menu.addAction("Subreddit Settings")
        subreddit_downloads = subreddit_menu.addAction("View Subreddit Downloads")
        subreddit_menu.addSeparator()
        open_subreddit_folder = subreddit_menu.addAction("Open Download Folder")
        subreddit_menu.addSeparator()
        add_subreddit = subreddit_menu.addAction("Add Subreddit")
        remove_subreddit = subreddit_menu.addAction("Remove Subreddit")

        if subreddit is not None:
            subreddit_menu.addSeparator()
            download_enabled_text = 'Enable Download' if not subreddit.enable_download else 'Disable Download'
            toggle_download_enabled = subreddit_menu.addAction(download_enabled_text)
            toggle_download_enabled.triggered.connect(subreddit.toggle_enable_download)

        add_subreddit.triggered.connect(self.add_subreddit_dialog)
        remove_subreddit.triggered.connect(self.remove_subreddit)
        subreddit_settings.triggered.connect(lambda: self.subreddit_settings(0, False))
        subreddit_downloads.triggered.connect(lambda: self.subreddit_settings(1, False))
        open_subreddit_folder.triggered.connect(self.open_subreddit_download_folder)

        if not valid:
            subreddit_settings.setVisible(False)
            subreddit_downloads.setVisible(False)
            open_subreddit_folder.setVisible(False)
            remove_subreddit.setVisible(False)

        if self.running:
            add_subreddit.setEnabled(False)
            remove_subreddit.setEnabled(False)

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
            user_settings_dialog = RedditObjectSettingsDialog(current_list_model,
                                                              current_list_model.reddit_object_list[position],
                                                              self.running)
            user_settings_dialog.single_download.connect(self.run_single_user)
            user_settings_dialog.show()
            if page == 1:
                user_settings_dialog.change_to_downloads_view()
            if not user_settings_dialog.closed:
                dialog = user_settings_dialog.exec_()
                if dialog == QtWidgets.QDialog.Accepted:
                    self.set_not_saved()
                    if user_settings_dialog.restore_defaults:
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
            self.logger.error('User settings unable to open', exc_info=True)

    def subreddit_settings(self, page, from_menu):
        """Operates the same as the user_settings function"""
        current_list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            if not from_menu:
                position = self.get_selected_view_index(self.subreddit_list_view).row()
            else:
                position = 0
            subreddit_settings_dialog = RedditObjectSettingsDialog(current_list_model,
                                                                   current_list_model.reddit_object_list[position],
                                                                   self.running)
            subreddit_settings_dialog.single_download.connect(self.run_single_subreddit)
            subreddit_settings_dialog.show()
            if page == 1:
                subreddit_settings_dialog.change_to_downloads_view()
            if not subreddit_settings_dialog.closed:
                dialog = subreddit_settings_dialog.exec_()
                if dialog == QtWidgets.QDialog.Accepted:
                    self.set_not_saved()
                    if not subreddit_settings_dialog.restore_defaults:
                        current_list_model.reddit_object_list = subreddit_settings_dialog.object_list
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
            self.logger.error('Subreddit settings unable to open', exc_info=True)

    def open_user_download_folder(self):
        """Opens the Folder where the users downloads are saved using the default file manager"""
        current_list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        selected_user = None
        try:
            position = self.get_selected_view_index(self.user_list_view).row()
            selected_user = current_list_model.reddit_object_list[position]
            SystemUtil.open_in_system(selected_user.save_directory)
            self.logger.info('User download folder opened', extra={'user': selected_user.name})
        except AttributeError:
            self.logger.error('Download folder tried to open with no user selected', exc_info=True)
            Message.no_reddit_object_selected(self, 'user')
        except FileNotFoundError:
            path = selected_user.save_directory if selected_user is not None else 'No Selected User'
            self.logger.error('Download folder tried to open with no download folder found',
                              extra={'selected_user_save_directory': path}, exc_info=True)
            Message.no_download_folder(self, 'user')

    def open_subreddit_download_folder(self):
        """Opens the Folder where the subreddit downloads are saved using the default file manager"""
        current_list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        selected_sub = None
        try:
            position = self.get_selected_view_index(self.subreddit_list_view).row()
            selected_sub = current_list_model.reddit_object_list[position]
            path = os.path.join(selected_sub.save_directory, selected_sub.name) if \
                selected_sub.subreddit_save_method.startswith('Subreddit') else selected_sub.save_directory
            SystemUtil.open_in_system(path)
        except AttributeError:
            self.logger.error('Download folder tried to open with no subreddit selected', exc_info=True)
            Message.no_reddit_object_selected(self, 'subreddit')
        except FileNotFoundError:
            path = selected_sub.save_direcory if selected_sub is not None else 'No Sub Selected'
            self.logger.error('Download folder tired to open with no download folder found',
                              extra={'selected_sub_save_directory': path}, exc_info=True)
            Message.no_download_folder(self, 'subreddit')

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
            if self.settings_manager.user_finder_run_with_main:
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
            self.logger.error('Run called with no items available to download', exc_info=True)
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
        self.logger.info('User download initiated', extra={'list_size': len(user_list),
                                                           'settings': self.settings_manager.json})
        self.download_runner = DownloadRunner(user_list, None, self.queue, None)
        self.start_reddit_extractor_thread('USER')

    def run_single_user(self, download_tuple):
        """
        Called from the user settings dialog and supplied the name of the selected user.  Downloads only the
        selected user
        """
        user = download_tuple[0]
        self.logger.info('Single user download initiated', extra={'user': user.name,
                                                                  'settings': self.settings_manager.json})
        self.started_download_gui_shift()
        user_list = [user]
        self.download_runner = DownloadRunner(user_list, None, self.queue, None)
        self.start_reddit_extractor_thread('USER')

    def run_subreddit(self):
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.logger.info('Subreddit download initiated', extra={'list_size': len(subreddit_list),
                                                                'settings': self.settings_manager.json})
        self.download_runner = DownloadRunner(None, subreddit_list, self.queue, None)
        self.start_reddit_extractor_thread('SUBREDDIT')

    def run_single_subreddit(self, download_tuple):
        """
        Called from the subreddit settings dialog and supplied the name of the selected subreddit.  Downloads only the
        selected subreddit
        """
        self.logger.info('Single subreddit download initiated', extra={'subreddit': download_tuple[0].name,
                                                                       'settings': self.settings_manager.json})
        self.started_download_gui_shift()
        subreddit_list = [download_tuple[0]]
        self.download_runner = DownloadRunner(None, subreddit_list, self.queue, None)
        self.download_runner.single_subreddit_run_method = download_tuple[1]
        self.start_reddit_extractor_thread('SUBREDDIT')

    def run_user_and_subreddit(self):
        """
        Downloads from the users in the user list only the content which has been posted to the subreddits in the
        subreddit list.
        """
        user_list = self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
        subreddit_list = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()].reddit_object_list
        self.logger.info('User and subreddit download initiated', extra={'user_list_size': len(user_list),
                                                                         'subreddit_list_size': len(subreddit_list),
                                                                         'settings': self.settings_manager.json})
        self.download_runner = DownloadRunner(user_list, subreddit_list, self.queue, None)
        self.start_reddit_extractor_thread('USERS_AND_SUBREDDITS')

    def run_unfinished_downloads(self):
        """Downloads the content that was left during the last run if the user clicked the stop download button"""
        self.logger.info('Unfinished downloads download initiated', extra={'list_size': len(self.unfinished_downloads),
                                                                           'settings': self.settings_manager.json})
        self.download_count = 0
        self.started_download_gui_shift()
        self.download_runner = DownloadRunner(None, None, self.queue, self.unfinished_downloads)
        self.start_reddit_extractor_thread('UNFINISHED')

    def start_reddit_extractor_thread(self, download_type):
        """Moves the extractor to a different thread and calls the appropriate function for the type of download"""
        self.stop_download.connect(self.download_runner.stop_download)
        self.thread = QtCore.QThread()
        self.download_runner.moveToThread(self.thread)
        if download_type == 'USER':
            self.thread.started.connect(self.download_runner.validate_users)
        elif download_type == 'SUBREDDIT':
            self.thread.started.connect(self.download_runner.validate_subreddits)
        elif download_type == 'USERS_AND_SUBREDDITS':
            self.thread.started.connect(self.download_runner.validate_users_and_subreddits)
        elif download_type == 'UNFINISHED':
            self.thread.started.connect(self.download_runner.finish_downloads)
        self.download_runner.remove_invalid_object.connect(self.remove_invalid_reddit_object)
        self.download_runner.downloaded_objects_signal.connect(self.fill_downloaded_objects_list)
        self.download_runner.failed_download_signal.connect(self.handle_failed_download_object)
        self.download_runner.setup_progress_bar.connect(self.setup_progress_bar)
        self.download_runner.update_progress_bar_signal.connect(self.update_progress_bar)
        self.download_runner.unfinished_downloads_signal.connect(self.set_unfinished_downloads)
        self.download_runner.finished.connect(self.thread.quit)
        self.download_runner.finished.connect(self.download_runner.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.finished_download_gui_shift)
        self.thread.start()
        self.logger.info('Downloader thread started')

    def handle_failed_download_object(self, failed_post):
        """
        Handles a post sent from the download runner that failed to be extracted or downloaded.
        :param failed_post: The post that failed to extract or download.
        :type failed_post: Post
        """
        self.failed_list.append(failed_post)

    def update_output(self, text):
        """
        Updates outputs the supplied text to the output box in the GUI.  Also supplies the content to update the status
        bar, failed download dialog box, and if the user finder is open, will emit a signal to update the user finder
        progress bar
        """
        if text.lower().startswith('fail'):
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
        self.settings_manager.total_files_downloaded += 1
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
                self.set_not_saved()
            else:
                self.logger.warning('Unable to add user list', extra={'invalid_name': new_user_list})
                Message.not_valid_name(self)

    def remove_user_list(self):
        try:
            if Message.remove_user_list(self):
                current_user_list = self.user_lists_combo.currentText()
                list_size = len(self.user_view_chooser_dict[current_user_list].reddit_object_list)
                del self.user_view_chooser_dict[current_user_list]
                self.user_lists_combo.removeItem(self.user_lists_combo.currentIndex())
                if self.user_lists_combo.currentText() != '':
                    self.user_list_view.setModel(self.user_view_chooser_dict[self.user_lists_combo.currentText()])
                    self.user_view_chooser_dict[
                        self.user_lists_combo.currentText()].sort_lists((self.list_sort_method, self.list_order_method))
                else:
                    self.user_list_view.setModel(None)
                self.refresh_user_count()
                self.set_not_saved()
                self.logger.info('User list removed', extra={'name': current_user_list, 'list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove user list: No user list available to remove', exc_info=True)
            Message.no_user_list(self)

    def change_user_list(self):
        """Changes the user list model based on the user_list_combo"""
        new_list_view = self.user_lists_combo.currentText()
        self.user_list_view.setModel(self.user_view_chooser_dict[new_list_view])
        self.user_view_chooser_dict[new_list_view].sort_lists((self.list_sort_method, self.list_order_method))
        self.refresh_user_count()
        self.set_not_saved()
        self.logger.info('User list changed to: %s' % new_list_view)

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
                self.set_not_saved()
            else:
                self.logger.warning('Unable to add subreddit list', extra={'invalid_name': new_subreddit_list},
                                    exc_info=True)
                Message.not_valid_name(self)

    def remove_subreddit_list(self):
        try:
            if Message.remove_subreddit_list(self):
                current_sub_list = self.subreddit_list_combo.currentText()
                list_size = len(self.subreddit_view_chooser_dict[current_sub_list].reddit_object_list)
                del self.subreddit_view_chooser_dict[current_sub_list]
                self.subreddit_list_combo.removeItem(self.subreddit_list_combo.currentIndex())
                if self.subreddit_list_combo.currentText() != '':
                    self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[
                                                          self.subreddit_list_combo.currentText()])
                    self.subreddit_view_chooser_dict[
                        self.subreddit_list_combo.currentText()].sort_lists((self.list_sort_method,
                                                                              self.list_order_method))
                else:
                    self.subreddit_list_view.setModel(None)
                self.refresh_subreddit_count()
                self.set_not_saved()
                self.logger.info('Subreddit list removed', extra={'name': current_sub_list, 'list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove subreddit list: No list to remove', exc_info=True)
            Message.no_subreddit_list(self)

    def change_subreddit_list(self):
        new_list_view = self.subreddit_list_combo.currentText()
        self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[new_list_view])
        self.subreddit_view_chooser_dict[new_list_view].sort_lists((self.list_sort_method, self.list_order_method))
        self.refresh_subreddit_count()
        self.set_not_saved()

    def add_user_dialog(self):
        """Opens the dialog to enter the user name"""
        if self.user_lists_combo != '' and len(self.user_view_chooser_dict) > 0:
            add_user_dialog = AddUserDialog('USER', self)
            dialog = add_user_dialog.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                if add_user_dialog.layout_style == 'SINGLE':
                    self.add_single_user(add_user_dialog.name)
                else:
                    self.add_multiple_users(add_user_dialog.object_name_list_model.name_list)
        else:
            Message.no_user_list(self)

    def add_single_user(self, new_user):
        try:
            list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
            user = self.make_user(new_user)
            reply = self.add_reddit_object_to_list(user, list_model)
            if reply == 'NAME_EXISTS':
                Message.name_in_list(self, new_user)
            elif reply == 'INVALID_NAME':
                Message.not_valid_name(self, new_user)
            else:
                self.refresh_user_count()
        except KeyError:
            Message.no_user_list(self)

    def add_multiple_users(self, user_list):
        try:
            existing_names = []
            invalid_names = []
            list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
            for name in user_list:
                user = self.make_user(name)
                reply = self.add_reddit_object_to_list(user, list_model)
                if reply == 'NAME_EXISTS':
                    existing_names.append(name)
                elif reply == 'INVALID_NAME':
                    invalid_names.append(name)
            self.refresh_user_count()
            if len(existing_names) > 0:
                Message.names_in_list(self, existing_names)
            if len(invalid_names) > 0:
                Message.invalid_names(self, invalid_names)
        except KeyError:
            Message.no_user_list(self)

    def add_reddit_object_to_list(self, reddit_object, list_model):
        """
        Adds the supplied reddit_object to the supplied list model.
        :param reddit_object: The reddit object that is to be added to the list.
        :param list_model: The list model that the reddit object is to be added to.
        :type reddit_object: RedditObject
        :type list_model: ListModel
        """
        if reddit_object.name != '' and ' ' not in reddit_object.name:
            if not list_model.check_name(reddit_object.name):
                list_model.insertRow(reddit_object)
                list_model.sort_lists((self.list_sort_method, self.list_order_method))
                self.set_not_saved()
                return 'ADDED'
            else:
                return 'NAME_EXISTS'
        else:
            return 'INVALID_NAME'

    def make_user(self, name):
        """
        Makes a new User object
        :param name: The name of the user object
        :return: A new user object with the supplied name
        """
        new_user = User(self.version, name, self.settings_manager.save_directory, self.settings_manager.post_limit,
                        self.settings_manager.avoid_duplicates, self.settings_manager.download_videos,
                        self.settings_manager.download_images, self.settings_manager.nsfw_filter,
                        self.settings_manager.name_downloads_by, datetime.now().timestamp())
        return new_user

    def remove_user(self):
        """
        Gets the currently selected index from the user list and the current user list model and calls a method to
        remove the object at the current index
        """
        list_model = self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        try:
            index = self.get_selected_view_index(self.user_list_view).row()
            self.remove_reddit_object(index, list_model)
        except AttributeError:
            pass

    def remove_reddit_object(self, index, list_model):
        """
        Removes the reddit object at the supplied index from the supplied list_model.
        :param index: The index of the reddit object to be removed.
        :param list_model: The list model that the reddit object is to be removed from.
        :type index: int
        :type list_model: ListModel
        """
        try:
            reddit_object = list_model.reddit_object_list[index]
            if Message.remove_reddit_object(self, reddit_object.name):
                list_model.removeRows(index, 1)
                self.set_not_saved()
        except (KeyError, AttributeError):
            self.logger.warning('Remove reddit object failed: No object selected', exc_info=True)
            Message.no_reddit_object_selected(self, list_model.list_type)

    def remove_invalid_reddit_object(self, reddit_object):
        """
        Handles removing the supplied reddit object if the downloader finds that the reddit object is not valid.  This
        method also renames the download folder.
        :param reddit_object: The reddit object (User or Subreddit) that is invalid and is to be removed.
        :type reddit_object: RedditObject
        """
        name = reddit_object.name
        if Message.reddit_object_not_valid(self, reddit_object.name, reddit_object.object_type):
            working_list = self.get_working_list(reddit_object.object_type)
            working_list.remove_reddit_object(reddit_object)
            if not SystemUtil.rename_directory_deleted(reddit_object.save_directory):
                rename_log = 'Failed'
                Message.failed_to_rename_error(self, reddit_object.name)
            else:
                rename_log = 'Success'
            self.refresh_object_count()
            self.set_not_saved()
            self.logger.info('Invalid reddit object removed', extra={'object_name': name,
                                                                     'folder_rename': rename_log})

    def get_working_list(self, object_type):
        if object_type == 'USER':
            return self.user_view_chooser_dict[self.user_lists_combo.currentText()]
        else:
            return self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]

    def add_subreddit_dialog(self):
        """See add_user_dialog"""
        if self.subreddit_list_combo != '' and len(self.subreddit_view_chooser_dict) > 0:
            add_sub_dialog = AddUserDialog('SUBREDDIT', self)
            add_sub_dialog.setWindowTitle('Add Subreddit Dialog')
            add_sub_dialog.label.setText('Enter a new subreddit:')
            dialog = add_sub_dialog.exec_()
            if dialog == QtWidgets.QDialog.Accepted:
                if add_sub_dialog.layout_style == 'SINGLE':
                    self.add_single_subreddit(add_sub_dialog.name)
                else:
                    self.add_multiple_subreddits(add_sub_dialog.object_name_list_model.name_list)
        else:
            Message.no_user_list(self)

    def add_single_subreddit(self, new_sub):
        try:
            list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
            subreddit = self.make_subreddit(new_sub)
            reply = self.add_reddit_object_to_list(subreddit, list_model)
            if reply == 'NAME_EXISTS':
                Message.name_in_list(self, new_sub)
            elif reply == 'INVALID_NAME':
                Message.not_valid_name(self, new_sub)
            else:
                self.refresh_user_count()
        except KeyError:
            Message.no_user_list(self)

    def add_multiple_subreddits(self, sub_list):
        try:
            existing_names = []
            invalid_names = []
            list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
            for name in sub_list:
                sub = self.make_subreddit(name)
                reply = self.add_reddit_object_to_list(sub, list_model)
                if reply == 'NAME_EXISTS':
                    existing_names.append(name)
                elif reply == 'INVALID_NAME':
                    invalid_names.append(name)
            self.refresh_subreddit_count()
            if len(existing_names) > 0:
                Message.names_in_list(self, existing_names)
            if len(invalid_names) > 0:
                Message.invalid_names(self, invalid_names)
        except KeyError:
            Message.no_user_list(self)

    def add_subreddit_to_list(self, new_sub):
        """
        Creates a new Subreddit object from the supplied subreddit name and adds the Subreddit to the current list
        model.
        :param new_sub: The name of the new sub which is to be added to the list_model.
        :type new_sub: str
        """
        list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            if new_sub != '' and new_sub != ' ':
                if list_model.check_name(new_sub):
                    self.logger.info('Unable to add subreddit: Name already in list', extra={'name': new_sub})
                    Message.name_in_list(self, new_sub)
                else:
                    sub = self.make_subreddit(new_sub)
                    self.add_reddit_object_to_list(sub, list_model)
                    self.refresh_subreddit_count()
            else:
                self.logger.warning('Unable to add subreddit: Invalid name', extra={'name': new_sub})
                Message.not_valid_name(self, new_sub)
        except KeyError:
            self.logger.warning('Unable to add subreddit: No subreddit list available', exc_info=True)
            Message.no_subreddit_list(self)

    def make_subreddit(self, name):
        """
        Makes a new subreddit object
        :param name: The name of the subreddit
        :return: A new subreddit object with the supplied name
        :rtype: Subreddit
        """
        new_sub = Subreddit(self.version, name, self.settings_manager.save_directory, self.settings_manager.post_limit,
                            self.settings_manager.avoid_duplicates, self.settings_manager.download_videos,
                            self.settings_manager.download_images, self.settings_manager.nsfw_filter,
                            self.settings_manager.save_subreddits_by, self.settings_manager.name_downloads_by,
                            datetime.now().timestamp())
        return new_sub

    def remove_subreddit(self):
        """
        Gets the currently selected index from the subreddit list and the current subreddit list model and calls a
        method to remove the object at the current index
        """
        list_model = self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
        try:
            index = self.get_selected_view_index(self.subreddit_list_view).row()
            self.remove_reddit_object(index, list_model)
        except AttributeError:
            pass

    def select_directory(self):
        """
        Opens a dialog for the user to select a directory then verifies and returns the selected directory if it exists,
        and returns None if it does not.
        :return: A path to a user selected directory.
        :rtype: str
        """
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select The Folder to Import From',
                                                                       self.settings_manager.save_directory))
        if os.path.isdir(folder):
            return folder
        else:
            Message.invalid_file_path(self)
            return None

    def get_selected_view_index(self, list_view):
        """Returns a single index if multiple are selected"""
        indicies = list_view.selectedIndexes()
        index = None
        if len(indicies) > 0:
            index = indicies[0]
        return index

    def fill_downloaded_objects_list(self, downloaded_object_dict):
        """Adds a users name to a list if they had content downloaded while the program is open"""
        self.last_downloaded_objects = downloaded_object_dict
        self.file_last_downloaded_list.setEnabled(True)

    def open_last_downloaded_list(self):
        """
        Opens a dialog that shows the downloads of any user that has been added to the last downloaded users list.
        """
        if len(self.last_downloaded_objects) > 0:
            obj_display_list = [user for user in
                                self.user_view_chooser_dict[self.user_lists_combo.currentText()].reddit_object_list
                                if user.name in self.last_downloaded_objects]
            obj_display_list.extend(sub for sub in
                                    self.subreddit_view_chooser_dict[self.subreddit_list_combo.currentText()]
                                    .reddit_object_list if sub.name in self.last_downloaded_objects)

            downloaded_objects_dialog = DownloadedObjectsDialog(obj_display_list, obj_display_list[0],
                                                                self.last_downloaded_objects)
            downloaded_objects_dialog.change_to_downloads_view()
            downloaded_objects_dialog.show()
        else:
            Message.no_users_downloaded(self)

    def started_download_gui_shift(self):
        """Disables certain options in the GUI that may be problematic if used while the downloader is running"""
        self.set_not_saved()
        self.running = True
        self.downloaded = 0
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
        if len(self.failed_list) > 0:
            self.file_failed_download_list.setEnabled(True)
            if self.settings_manager.auto_display_failed_list:
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
        """Displays the main settings dialog and calls methods that update each reddit object if needed."""
        settings = RedditDownloaderSettingsGUI()
        settings.show()
        dialog = settings.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.update_user_settings()
            self.update_subreddit_settings()

    def update_user_settings(self):
        """Iterates through the user list and calls update settings for each user"""
        self.set_not_saved()
        updated = 0
        total = 0
        for value in self.user_view_chooser_dict.values():
            for user in value.reddit_object_list:
                total += 1
                if not user.do_not_edit:
                    updated += 1
                    self.update_object_settings(user)
        self.logger.info('User settings updated', extra={'updated_users': updated, 'total_users': total})

    def update_subreddit_settings(self):
        """Iterates through the subreddit list and calls update settings for each sub"""
        self.set_not_saved()
        updated = 0
        total = 0
        for value in self.subreddit_view_chooser_dict.values():
            for sub in value.reddit_object_list:
                total += 1
                if not sub.do_not_edit:
                    updated += 1
                    self.update_object_settings(sub)
                    sub.subreddit_save_method = self.settings_manager.save_subreddits_by
        self.logger.info('Subreddit settings updated', extra={'updated_subreddits': updated, 'total_subreddits': total})

    def update_object_settings(self, reddit_object):
        """Updates object specific settings for the supplied object"""
        reddit_object.post_limit = self.settings_manager.post_limit
        reddit_object.save_path = self.settings_manager.save_directory
        reddit_object.name_downloads_by = self.settings_manager.name_downloads_by
        reddit_object.avoid_duplicates = self.settings_manager.avoid_duplicates
        reddit_object.download_videos = self.settings_manager.download_videos
        reddit_object.download_images = self.settings_manager.download_images
        self.update_custom_dates(reddit_object)

    def update_custom_dates(self, reddit_object):
        """Updates the custom date attribute of the supplied reddit object."""
        if self.settings_manager.restrict_by_custom_date:
            reddit_object.custom_date_limit = self.settings_manager.custom_date
        else:
            reddit_object.custom_date_limit = None

    def display_failed_downloads(self):
        """Opens a dialog with information about any content that was not able to be downloaded for whatever reason"""
        failed_dialog = FailedDownloadsDialog(self.failed_list)
        failed_dialog.auto_display_checkbox.setChecked(not self.settings_manager.auto_display_failed_list)
        failed_dialog.show()
        dialog = failed_dialog.exec_()
        if dialog == QtWidgets.QDialog.Accepted:
            self.settings_manager.auto_display_failed_list = not failed_dialog.auto_display_checkbox.isChecked()

    # def display_user_finder(self, auto):
    #     """Opens the UserFinder dialog"""
    #     self.user_finder_open = True
    #     self.file_open_user_finder.setEnabled(False)
    #     all_existing_users = []
    #     for value in self.user_view_chooser_dict.values():
    #         for user in value.reddit_object_list:
    #             all_existing_users.append(user.name)
    #     user_lists = self.user_view_chooser_dict.keys()
    #     user_finder = UserFinderGUI(all_existing_users, user_lists, self.save_path, self.imgur_client, self.queue)
    #     # user_finder.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    #     user_finder.watchlist_when_run_checkbox_2.setChecked(self.run_user_finder_auto)
    #     user_finder.add_user_to_list.connect(self.add_found_user)
    #     self.update_user_finder.connect(user_finder.update_progress_bar)
    #     user_finder.closed.connect(self.user_finder_closed)
    #     if auto:
    #         user_finder.auto_opened = True
    #         user_finder.run()
    #     user_finder.show()
    #     if user_finder.exec_() == QtWidgets.QDialog.Accepted:
    #         self.run_user_finder_auto = user_finder.watchlist_when_run_checkbox_2.isChecked()
    #
    # def user_finder_closed(self):
    #     self.user_finder_open = False
    #     self.file_open_user_finder.setEnabled(True)
    #
    # def update_user_finder_progress_bar(self):
    #     self.update_user_finder.emit()

    def display_user_finder(self, auto):
        pass
        # self.user_finder = UserFinderGUI(self.user_view_chooser_dict)
        # self.user_finder.closed.connect(self.close_user_finder)
        # self.user_finder.show()

    def close_user_finder(self):
        self.user_finder = None

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
        try:
            imgur_client = ImgurUtils.get_new_client()
        except:
            self.logger.error('Failed to display imgur client information', exc_info=True)
            imgur_client = None

        if imgur_client is not None:
            credits_dict = imgur_client.credits
            dialog_text = 'Application credit limit: %s\nApplication credits remaining: %s\n\nUser credit limit: %s' \
                          '\nUser credits remaining: %s\nTime user credits reset: %s' %\
                          (credits_dict['ClientLimit'], credits_dict['ClientRemaining'], credits_dict['UserLimit'],
                           credits_dict['UserRemaining'],
                           datetime.strftime(datetime.fromtimestamp(int(credits_dict['UserReset'])),
                                             '%m-%d-%Y at %I:%M %p'))
            self.logger.info('Imgur client info calculated',
                             extra={'remaining_app_credits': credits_dict['ClientRemaining'],
                                    'remaining_user_credits': credits_dict['UserRemaining']})
            reply = QtWidgets.QMessageBox.information(self, 'Imgur Credits', dialog_text, QtWidgets.QMessageBox.Ok)

    def get_imgur_client(self):
        try:
            return ImgurUtils.get_client()
        except:
            self.logger.error('Failed to display imgur client information', exc_info=True)

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
            SystemUtil.open_in_system(file)
        except FileNotFoundError:
            self.logger.error('Unable to open user manual: Manual file not found', exc_info=True)
            Message.user_manual_not_found(self)

    def refresh_object_count(self):
        self.refresh_user_count()
        self.refresh_subreddit_count()

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
        self.set_not_saved()

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
        if self.check_unfinished_downloads() and self.check_save_status():
            self.close()
        else:
            QCloseEvent.ignore()

    def close_from_menu(self):
        if self.check_unfinished_downloads() and self.check_save_status():
            self.close()

    def check_unfinished_downloads(self):
        if self.unfinished_downloads_available:
            unfinished_dialog = UnfinishedDownloadsWarning()
            dialog = unfinished_dialog.exec_()
            return dialog == QtWidgets.QMessageBox.Accepted
        else:
            return True

    def check_save_status(self):
        if self.settings_manager.auto_save:
            self.save_state()
            return True
        elif not self.saved:
            ret = Message.unsaved_close_message(self)
            if ret == "SAVE":
                self.save_state()
                return True
            elif ret == "CLOSE":
                return True
            else:
                return False
        else:
            return True

    def close(self):
        self.receiver.stop_run()
        self.save_main_window_settings()
        super().close()

    def save_main_window_settings(self):
        self.settings_manager.main_window_geom = self.saveGeometry()
        self.settings_manager.horz_splitter_state = self.horz_splitter.saveState()
        self.settings_manager.vert_splitter_state = self.vert_splitter.saveState()
        self.settings_manager.list_sort_method = self.list_sort_method
        self.settings_manager.list_order_method = self.list_order_method
        self.settings_manager.download_users = self.download_users_checkbox.isChecked()
        self.settings_manager.download_subreddits = self.download_subreddit_checkbox.isChecked()
        self.settings_manager.save_main_window()

    def load_state(self):
        reddit_object_list = ObjectStateHandler.load_pickled_state()
        if reddit_object_list is False:
            Message.save_file_permission_denied(self, ObjectStateHandler.get_save_path())
        else:
            try:
                last_user_view = reddit_object_list['last_user_view']
                last_subreddit_view = reddit_object_list['last_sub_view']
                self.user_view_chooser_dict = reddit_object_list['user_dict']
                self.subreddit_view_chooser_dict = reddit_object_list['sub_dict']

                for name in self.user_view_chooser_dict.keys():
                    self.user_lists_combo.addItem(name)
                for name in self.subreddit_view_chooser_dict.keys():
                    self.subreddit_list_combo.addItem(name)
                self.user_lists_combo.setCurrentText(last_user_view)
                self.subreddit_list_combo.setCurrentText(last_subreddit_view)
                self.set_last_view_model('USER', last_user_view)
                self.set_last_view_model('SUB', last_subreddit_view)
                self.logger.info('Save_file successfully loaded into gui')
            except KeyError:
                self.logger.error('Load state key error', exc_info=True)
            except TypeError:
                self.logger.error('Load state error: No save file found', exc_info=True)

    def set_last_view_model(self, view_dict, last_view):
        try:
            if view_dict == 'USER':
                self.user_list_view.setModel(self.user_view_chooser_dict[last_view])
            else:
                self.subreddit_list_view.setModel(self.subreddit_view_chooser_dict[last_view])
        except KeyError:
            pass

    def save_state(self):
        """Pickles the user and subreddit lists and saves any settings that need to be saved"""
        self.settings_manager.save_all()
        save_object_dict = {
            'user_view_chooser_dict': self.user_view_chooser_dict,
            'sub_view_chooser_dict': self.subreddit_view_chooser_dict,
            'current_user_view': self.user_lists_combo.currentText(),
            'current_sub_view': self.subreddit_list_combo.currentText()
        }
        if not ObjectStateHandler.save_pickled_state(save_object_dict):
            Message.failed_to_save(self)
            self.set_not_saved()
        else:
            self.set_saved()

    def import_save_file(self):
        """
        Has the user select a save file, then moves the file to the applications data folder.  If a save file already
        exists, the user is asked if they want to overwrite.  If the file is successfully moved, load_state is called
        to load up the new save file.
        """
        imported = False
        save_file = self.select_save_file()
        if save_file is not None:
            file_name = self.get_file_name(save_file)
            if file_name == 'save_file':
                folder = os.path.dirname(save_file)
                if self.move_save_files(folder, True):
                    imported = True
                    self.logger.info('Save file imported')
                else:
                    if Message.overwrite_save_file_question(self):
                        imported = self.move_save_files(folder, False)
                        self.logger.info('Save file imported: Old save file overwritten')
            if imported:
                self.load_new_save_file()

    def load_new_save_file(self):
        """Clears the list names from the list chooser combos and loads the newly moved save file into the GUI"""
        self.user_lists_combo.clear()
        self.subreddit_list_combo.clear()
        self.load_state()

    def move_save_files(self, source_folder, first_attempt):
        """
        Attemps to move any file in the supplied source with the name 'save_file' to the applications data folder.
        :param source_folder: The folder in which the save_file the user selected resides.
        :param first_attempt: Indicates if this is the first or second attempt to move files. Determines if existing
                              save files will be overwritten.
        :type source_folder: str
        :type first_attempt: bool
        :return: True if the move was successful and False if it was not.
        :rtype: bool
        """
        try:
            for file in os.listdir(source_folder):
                if self.get_file_name(file) == 'save_file':
                    new_path = os.path.join(SystemUtil.get_data_directory(), file)
                    if os.path.isfile(new_path) and not first_attempt:
                        os.remove(new_path)
                    else:
                        return False
                    SystemUtil.import_data_file(source_folder, file)
            return True
        except FileExistsError:
            self.logger.error('Failed to move save file: File already exists',
                              extra={'source_folder': source_folder}, exc_info=True)
            self.update_output('Error: Failed to import save file: Existing save file could not be overwritten')
            return False

    def select_save_file(self):
        """
        Opens a dialog for the user to select a file then verifies and returns the selected file if it exists, and
        returns None if it does not.
        :return: A path to a user selected file.
        :rtype: str
        """
        file = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.path.expanduser('~'))[0])
        if file != '':
            if os.path.isfile(file):
                return file
            else:
                Message.invalid_file_path(self)
        return None

    def get_file_name(self, path):
        """Extracts only the file name without extension from the supplied file path."""
        name = os.path.basename(path)
        return os.path.splitext(name)[0]

    def open_save_file_location(self):
        """
        Opens the applications data directory in the default system file manager.
        """
        try:
            SystemUtil.open_in_system(SystemUtil.get_data_directory())
        except Exception:
            self.logger.error('Failed to open data directory', exc_info=True)

    def check_for_updates(self, from_menu):
        """
        Opens and runs the update checker on a separate thread. Sets self.from_menu so that other dialogs know the
        updater has been ran by the user, this will result in different dialog behaviour
        """
        self.update_thread = QtCore.QThread()
        self.update_checker = UpdateChecker(self.version)
        self.update_checker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_checker.run)
        if from_menu:
            self.update_checker.update_available_signal.connect(self.update_dialog)
            self.update_checker.no_update_signal.connect(self.no_update_available_dialog)
        else:
            self.update_checker.update_available_signal.connect(self.display_update)
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
        update_checker.exec_()

    def no_update_available_dialog(self):
        Message.up_to_date_message(self)
