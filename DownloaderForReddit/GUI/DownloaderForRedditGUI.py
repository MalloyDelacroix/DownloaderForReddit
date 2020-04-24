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
from PyQt5.QtWidgets import (QMainWindow, QActionGroup, QAbstractItemView, QProgressBar, QLabel, QMenu, QInputDialog,
                             QFileDialog, QDialog, QMessageBox)
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import logging

from ..GUI_Resources.DownloaderForRedditGUI_auto import Ui_MainWindow
from ..GUI.AboutDialog import AboutDialog
from ..GUI.FailedDownloadsDialog import FailedDownloadsDialog
from ..GUI.RedditObjectSettingsDialog import RedditObjectSettingsDialog
from ..GUI.UnfinishedDownloadsDialog import UnfinishedDownloadsDialog
from ..GUI.UpdateDialogGUI import UpdateDialog
from ..GUI.Messages import Message
from ..GUI.DownloaderForRedditSettingsGUI import RedditDownloaderSettingsGUI
from ..GUI.AddRedditObjectDialog import AddRedditObjectDialog
from ..GUI.DownloadSessionDialog import DownloadSessionDialog
from ..GUI.FfmpegInfoDialog import FfmpegInfoDialog
from ..Core.DownloadRunner import DownloadRunner
from ..Core.RedditObjectCreator import RedditObjectCreator
from ..Database.Models import User, Subreddit, RedditObject, RedditObjectList
from ..Utils.UpdaterChecker import UpdateChecker
from ..Utils import Injector, SystemUtil, ImgurUtils, VideoMerger
from ..Utils.Exporters import TextExporter, JsonExporter
from ..Utils.TokenParser import TokenParser
from ..ViewModels.RedditObjectListModel import RedditObjectListModel
from ..version import __version__


class DownloaderForRedditGUI(QMainWindow, Ui_MainWindow):

    stop_download_signal = pyqtSignal(bool)  # bool indicates whether the stop is a hard stop or not

    def __init__(self, queue, receiver):
        """
        The main GUI window that all interaction is done through.

        :param queue: An instance of the queue initialized in the "main" function and passed to the main GUI window in
         order to update the main GUI output box.
        :param receiver: The receiver that is initialized in the "main" function and moved to another thread.  This
        keeps the queue updated with fresh output from all throughout the program.
        """
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.version = __version__
        self.failed_list = []
        self.last_downloaded_objects = {}
        self.potential_downloads = 0
        self.downloaded = 0
        self.progress_limit = 0
        self.progress = 0
        self.running = False
        self.db_handler = Injector.get_database_handler()

        # region Settings
        self.settings_manager = Injector.get_settings_manager()

        geom = self.settings_manager.main_window_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.horz_splitter.setSizes(self.settings_manager.horizontal_splitter_state)
        self.list_sort_method = self.settings_manager.list_sort_method
        self.list_order_method = self.settings_manager.list_order_method

        if self.settings_manager.download_radio_state == 'USER':
            self.download_users_radio.setChecked(True)
        elif self.settings_manager.download_radio_state == 'SUBREDDIT':
            self.download_subreddits_radio.setChecked(True)
        else:
            self.constain_to_sub_list_radio.setChecked(True)
        # endregion

        self.queue = queue
        self.receiver = receiver

        # region Main Menu

        # region File Menu
        self.open_settings_menu_item.triggered.connect(self.open_settings_dialog)
        self.open_data_directory_menu_item.triggered.connect(self.open_data_directory)
        self.exit_menu_item.triggered.connect(self.close_from_menu)
        # endregion

        # region View Menu
        self.list_view_group = QtWidgets.QActionGroup(self)
        self.list_view_group.addAction(self.sort_list_by_name_menu_item)
        self.list_view_group.addAction(self.sort_list_by_date_added_menu_item)
        self.list_view_group.addAction(self.sort_list_by_post_count_menu_item)
        self.sort_list_by_name_menu_item.triggered.connect(lambda: self.set_list_sort_method(0))
        self.sort_list_by_date_added_menu_item.triggered.connect(lambda: self.set_list_sort_method(1))
        self.sort_list_by_post_count_menu_item.triggered.connect(lambda: self.set_list_sort_method(2))

        self.list_view_order = QtWidgets.QActionGroup(self)
        self.list_view_order.addAction(self.sort_list_ascending_menu_item)
        self.list_view_order.addAction(self.sort_list_descending_menu_item)
        self.sort_list_ascending_menu_item.triggered.connect(lambda: self.set_list_order_method(0))
        self.sort_list_descending_menu_item.triggered.connect(lambda: self.set_list_order_method(1))
        self.set_view_menu_items_checked()

        self.download_session_menu_item.triggered.connect(self.open_download_sessions_dialog)
        # endregion

        # region Lists Menu
        self.add_user_list_menu_item.triggered.connect(self.add_user_list)
        self.remove_user_list_menu_item.triggered.connect(self.remove_user_list)
        self.add_subreddit_list_menu_item.triggered.connect(self.add_subreddit_list)
        self.remove_subreddit_list_menu_item.triggered.connect(self.remove_subreddit_list)

        self.export_user_list_as_text_menu_item.triggered.connect(self.export_user_list_to_text)
        self.export_user_list_as_json_menu_item.triggered.connect(self.export_user_list_to_json)

        self.export_sub_list_as_text_menu_item.triggered.connect(self.export_subreddit_list_to_text)
        self.export_sub_list_as_json_menu_item.triggered.connect(self.export_subreddit_list_to_json)

        self.failed_download_list_menu_item.triggered.connect(self.display_failed_downloads)
        self.unfinished_downloads_menu_item.triggered.connect(self.display_unfinished_downloads_dialog)
        # endregion

        # region Download Menu
        self.download_user_list_menu_item.triggered.connect(self.download_user_list)
        self.download_subreddit_list_menu_item.triggered.connect(self.download_subreddit_list)
        self.download_user_list_constrained_menu_item.triggered.connect(self.download_user_list_constrained)
        # endregion

        # region Help Menu
        self.imgur_credit_dialog_menu_item.triggered.connect(self.display_imgur_client_information)
        self.user_manual_menu_item.triggered.connect(self.open_user_manual)
        self.ffmpeg_requirement_dialog_menu_item.triggered.connect(self.display_ffmpeg_info_dialog)
        self.check_for_updates_menu_item.triggered.connect(lambda: self.check_for_updates(True))
        self.about_menu_item.triggered.connect(self.display_about_dialog)
        # endregion

        # endregion

        self.user_list_model = RedditObjectListModel('USER')
        self.user_list_model.reddit_object_added.connect(self.check_new_object_for_download)
        self.user_list_view.setModel(self.user_list_model)
        self.subreddit_list_model = RedditObjectListModel('SUBREDDIT')
        self.subreddit_list_model.reddit_object_added.connect(self.check_new_object_for_download)
        self.subreddit_list_view.setModel(self.subreddit_list_model)

        self.load_state()

        self.refresh_user_count()
        self.refresh_subreddit_count()

        self.download_button.clicked.connect(self.run_full_download)
        self.soft_stop_download_button.clicked.connect(lambda: self.stop_download_signal.emit(False))
        self.terminate_download_button.clicked.connect(lambda: self.stop_download_signal.emit(True))
        self.shift_download_buttons()

        self.add_user_button.clicked.connect(self.add_user)
        self.remove_user_button.clicked.connect(self.remove_user)
        self.add_subreddit_button.clicked.connect(self.add_subreddit)
        self.remove_subreddit_button.clicked.connect(self.remove_subreddit)

        self.user_lists_combo.activated.connect(self.change_user_list)
        self.subreddit_list_combo.activated.connect(self.change_subreddit_list)

        self.user_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_list_view.customContextMenuRequested.connect(lambda: self.reddit_object_list_context_menu('USER'))

        self.user_list_view.doubleClicked.connect(lambda: self.user_settings(self.get_selected_single_user()))
        self.user_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.user_lists_combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_lists_combo.customContextMenuRequested.connect(self.user_list_combo_context_menu)

        self.subreddit_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subreddit_list_view.customContextMenuRequested.connect(
            lambda: self.reddit_object_list_context_menu('SUBREDDIT'))

        self.subreddit_list_view.doubleClicked.connect(
            lambda: self.subreddit_settings(self.get_selected_single_subreddit()))
        self.subreddit_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.subreddit_list_combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subreddit_list_combo.customContextMenuRequested.connect(self.subreddit_list_combo_context_menu)

        self.progress_bar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.statusbar.addPermanentWidget(self.progress_label)
        self.progress_label.setText('Extraction Complete')
        self.progress_label.setVisible(False)

        # self.check_ffmpeg()
        # self.check_for_updates(False)  TODO: re-enable this
        self.open_object_dialogs = []

    def get_selected_single_user(self):
        """
        Returns a single user that is selected from the user list.  If multiple users are selected, this method returns
        the first user in the selection list.  Used for when only one selection is applicable to the function that
        item selection is being used for (ie: opening the settings dialog for a user)
        :return: A single user selected from the user list.
        """
        indices = self.user_list_view.selectedIndexes()
        if len(indices) <= 0:
            return None
        else:
            return self.user_list_model.data(indices[0], Qt.UserRole)

    def get_selected_users(self):
        indices = self.user_list_view.selectedIndexes()
        selection_list = [self.user_list_model.data(index, Qt.UserRole) for index in indices]
        return selection_list

    def get_selected_user_ids(self):
        return [x.id for x in self.get_selected_users()]

    def get_selected_single_subreddit(self):
        """See get_selected_single_user"""
        indices = self.subreddit_list_view.selectedIndexes()
        if len(indices) <= 0:
            return None
        else:
            return self.subreddit_list_model.data(indices[0], Qt.UserRole)

    def get_selected_subreddits(self):
        indices = self.subreddit_list_view.selectedIndexes()
        selection_list = [self.subreddit_list_model.data(index, Qt.UserRole) for index in indices]
        return selection_list

    def get_selected_subreddit_ids(self):
        return [x.id for x in self.get_selected_subreddits()]

    def reddit_object_list_context_menu(self, object_type):
        menu = QMenu()
        try:
            if object_type == 'USER':
                ros = self.get_selected_users()
            else:
                ros = self.get_selected_subreddits()
        except AttributeError:
            ros = []

        if object_type == 'USER':
            ros = self.get_selected_users()
            open_settings_command = self.user_settings
            add_command = self.add_user
            remove_command = self.remove_user
        else:
            ros = self.get_selected_subreddits()
            open_settings_command = self.subreddit_settings
            add_command = self.add_subreddit
            remove_command = self.remove_subreddit

        try:
            enabled = ros[0].download_enabled
            download_text = \
                f'Download {ros[0].name}' if len(ros) == 1 else f'Download {len(ros)} {object_type.title()}s'
        except IndexError:
            enabled = False
            download_text = 'Download'

        open_settings = menu.addAction('Settings', lambda: open_settings_command(ros))
        menu.addSeparator()
        open_downloads = menu.addAction('Open Download Folder',
                                        lambda: self.open_reddit_object_download_folder(ros[0]))
        menu.addSeparator()
        add_object = menu.addAction(f'Add {object_type.title()}', add_command)
        remove_object = menu.addAction(f'Remove {object_type.title()}', remove_command)
        menu.addSeparator()
        disable_enable_download_option = False
        if all(x.download_enabled == enabled for x in ros):
            enabled_text = 'Enable Download' if not enabled else 'Disable Download'
        else:
            disable_enable_download_option = True
            enabled_text = 'Differing Download Enabled States'
        enable_download = menu.addAction(enabled_text,
                                         lambda: self.set_selection_attribute(ros, 'download_enabled', not enabled))
        download = menu.addAction(download_text, lambda: self.add_to_download(*[x.id for x in ros]))

        for action in menu.actions():
            if action != add_object:
                action.setDisabled(len(ros) <= 0)
        enable_download.setDisabled(disable_enable_download_option)

        menu.exec_(QCursor.pos())

    def set_selection_attribute(self, selected, attr, value):
        for x in selected:
            setattr(x, attr, value)

    def user_list_combo_context_menu(self):
        menu = QMenu()
        add_list = menu.addAction('Add User List')
        remove_list = menu.addAction('Remove User List')
        add_list.triggered.connect(self.add_user_list)
        remove_list.triggered.connect(self.remove_user_list)
        menu.exec(QCursor.pos())

    def subreddit_list_combo_context_menu(self):
        menu = QMenu()
        add_list = menu.addAction('Add Subreddit List')
        remove_list = menu.addAction('Remove Subreddit List')
        add_list.triggered.connect(self.add_subreddit_list)
        remove_list.triggered.connect(self.remove_subreddit_list)
        menu.exec(QCursor.pos())

    def user_settings(self, users):
        """
        Opens the RedditObjectSettingsDialog and sets the supplied user as the selected user to display the settings
        for.  The current user list is also taken by the dialog and the names shown in the additional objects list.
        :param users: A list of users that is to be set as the currently selected users list in the settings dialog.
        """
        if users is None:
            users = [self.user_list_model.reddit_objects[0]]
        id_list = [x.id for x in users]
        dialog = RedditObjectSettingsDialog('USER', self.user_list_model.list.name, selected_object_ids=id_list)
        dialog.download_signal.connect(self.add_to_download)
        dialog.show()
        dialog.exec_()

    def subreddit_settings(self, subreddits):
        """Operates the same as the user_settings function"""
        if subreddits is None:
            subreddits = [self.subreddit_list_model.reddit_objects[0]]
        id_list = [x.id for x in subreddits]
        dialog = RedditObjectSettingsDialog('SUBREDDIT', self.subreddit_list_model.list.name,
                                            selected_object_ids=id_list)
        dialog.download_signal.connect(self.add_to_download)
        dialog.show()
        dialog.exec_()

    def get_reddit_object_download_folder(self, reddit_object: RedditObject):
        sub_path = TokenParser.parse_tokens(reddit_object, reddit_object.post_save_structure)
        if reddit_object.object_type == 'USER':
            base_path = self.settings_manager.user_save_directory
        else:
            base_path = self.settings_manager.subreddit_save_directory
        return os.path.join(base_path, sub_path)

    def open_reddit_object_download_folder(self, reddit_object: RedditObject):
        try:
            path = self.get_reddit_object_download_folder(reddit_object)
            SystemUtil.open_in_system(path)
        except FileNotFoundError:
            Message.no_download_folder(self, reddit_object.object_type.lower())

    def run_full_download(self):
        if self.download_users_radio.isChecked():
            self.download_user_list()
        elif self.download_subreddits_radio.isChecked():
            self.download_subreddit_list()
        else:
            self.download_user_list_constrained()

    def download_user_list(self):
        user_id_list = self.user_list_model.get_id_list()
        self.run(user_id_list, None)

    def download_subreddit_list(self):
        sub_id_list = self.subreddit_list_model.get_id_list()
        self.run(None, sub_id_list)

    def download_user_list_constrained(self):
        user_id_list = self.user_list_model.get_id_list()
        sub_id_list = self.subreddit_list_model.get_id_list()
        self.run(user_id_list, sub_id_list)

    def run(self, user_id_list, sub_id_list, reddit_object_id_list=None):
        self.started_download_gui_shift()
        self.download_runner = DownloadRunner(user_id_list, sub_id_list, reddit_object_id_list)
        self.stop_download_signal.connect(self.download_runner.stop_download)
        self.thread = QThread()
        self.download_runner.moveToThread(self.thread)
        self.thread.started.connect(self.download_runner.run)

        self.download_runner.remove_invalid_object.connect(self.remove_invalid_reddit_object)
        self.download_runner.remove_forbidden_object.connect(self.remove_forbidden_reddit_object)
        self.download_runner.finished.connect(self.thread.quit)
        self.download_runner.finished.connect(self.download_runner.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.finished_download_gui_shift)
        self.thread.start()
        self.logger.info('Download thread started')

    def add_to_download(self, *args: int):
        """
        Adds a list of reddit object id's to a current download session if there is one active, otherwise starts a
        download session with the supplied id's.
        :param args: Reddit object id's that are to be downloaded
        """
        if self.running:
            for ro_id in args:
                self.download_runner.reddit_object_queue.put(ro_id)
        else:
            self.run(user_id_list=None, sub_id_list=None, reddit_object_id_list=args)

    def handle_failed_download_object(self, failed_post):
        """
        Handles a post sent from the download runner that failed to be extracted or downloaded.
        :param failed_post: The post that failed to extract or download.
        :type failed_post: Post
        """
        self.failed_list.append(failed_post)

    def update_output(self, text):
        self.output_box.append(text)

    def handle_potential_extraction(self):
        self.extend_progress()

    def handle_extraction(self):
        self.update_progress()

    def handle_potential_download(self):
        self.extend_progress()
        self.potential_downloads += 1
        self.update_status_bar()

    def handle_download(self):
        self.update_progress()
        self.downloaded += 1
        self.update_status_bar()

    def handle_extraction_error(self, error_message):
        self.extend_progress(forward=False)
        # TODO: inform user somehow

    def handle_download_error(self, error_message):
        self.extend_progress(forward=False)
        self.potential_downloads -= 1
        self.update_status_bar()
        # TODO: inform user somehow

    def update_status_bar(self):
        self.statusbar.showMessage(f'Downloaded: {self.downloaded} of {self.potential_downloads}', -1)

    def init_progress_bar(self):
        self.progress_limit = 0
        self.progress = 0
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

    def extend_progress(self, forward=True):
        if forward:
            self.progress_limit += 1
        else:
            self.progress_limit -= 1
        self.progress_bar.setMaximum(self.progress_limit)

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)

    def add_user_list(self, *, list_name=None):
        if list_name is None:
            list_name = self.get_list_name('USER')
        if list_name is not None:
            if list_name != '':
                added = self.user_list_model.add_new_list(list_name, 'USER')
                if added:
                    self.user_lists_combo.addItem(list_name)
                    self.user_lists_combo.setCurrentText(list_name)
                    self.refresh_user_count()
                else:
                    text = f'A user list already exists with the name "{list_name}"'
                    Message.generic_message(self, title='List Name Exists', text=text)
            else:
                self.logger.warning('Unable to add user list', extra={'invalid_name': list_name}, exc_info=True)
                Message.not_valid_name(self)

    def get_list_name(self, object_type):
        """
        Opens a dialog for the user to enter a name for a new user or subreddit list.  The dialog text is altered
        depending on the list type string that is provided.
        :param object_type: The type of object that the list will hold.
        """
        list_name, ok = QInputDialog.getText(
            self, f'New {object_type.capitalize()} List Dialog', f'Enter the new {object_type.lower()} list:')
        if ok:
            if list_name is not None and list_name != '':
                return list_name
        return None

    def remove_user_list(self):
        try:
            if Message.remove_user_list(self):
                current_user_list = self.user_lists_combo.currentText()
                list_size = self.user_list_model.rowCount()
                self.user_list_model.delete_current_list()
                self.user_lists_combo.removeItem(self.user_lists_combo.currentIndex())
                if self.user_lists_combo.currentText() != '':
                    self.user_list_model.set_list(self.user_lists_combo.currentText())
                    self.user_list_model.sort_list(self.list_sort_method, self.list_order_method)
                self.refresh_user_count()
                self.logger.info('User list removed', extra={'list_name': current_user_list,
                                                             'previous_list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove user list: No user list available to remove', exc_info=True)
            Message.no_user_list(self)

    def change_user_list(self):
        """Changes the user list model based on the user_list_combo"""
        new_list_name = self.user_lists_combo.currentText()
        self.user_list_model.set_list(new_list_name)
        self.user_list_model.sort_list(self.list_sort_method, self.list_order_method)
        self.refresh_user_count()
        self.logger.info('User list changed to: %s' % new_list_name)

    def export_user_list_to_text(self):
        current_list = self.user_lists_combo.currentText()
        file_path = self.get_file_path(current_list, 'Text Files (*.txt)')
        if file_path is not None:
            TextExporter.export_reddit_objects_to_text(self.user_list_model.list, file_path)

    def export_user_list_to_json(self):
        current_list = self.user_lists_combo.currentText()
        file_path = self.get_file_path(current_list, 'Json Files (*.json)')
        if file_path is not None:
            JsonExporter.export_reddit_objects_to_json(self.user_list_model.list, file_path)

    def add_subreddit_list(self, *, list_name=None):
        if list_name is None:
            list_name = self.get_list_name('SUBREDDIT')
        if list_name is not None:
            if list_name != '':
                added = self.subreddit_list_model.add_new_list(list_name, 'SUBREDDIT')
                if added:
                    self.subreddit_list_combo.addItem(list_name)
                    self.subreddit_list_combo.setCurrentText(list_name)
                    self.refresh_subreddit_count()
                else:
                    text = f'A subreddit list already exists with the name "{list_name}"'
                    Message.generic_message(self, title='List Name Exists', text=text)
            else:
                self.logger.warning('Unable to add subreddit list', extra={'invalid_name': list_name},
                                    exc_info=True)
                Message.not_valid_name(self)

    def remove_subreddit_list(self):
        try:
            if Message.remove_subreddit_list(self):
                current_sub_list = self.subreddit_list_combo.currentText()
                list_size = self.subreddit_list_model.rowCount()
                self.subreddit_list_model.delete_current_list()
                self.subreddit_list_combo.removeItem(self.subreddit_list_combo.currentIndex())
                if self.subreddit_list_combo.currentText() != '':
                    self.subreddit_list_model.set_list(self.subreddit_list_combo.currentText())
                    self.subreddit_list_model.sort_list(self.list_sort_method, self.list_order_method)
                self.refresh_subreddit_count()
                self.logger.info('Subreddit list removed', extra={'list_name': current_sub_list,
                                                                  'previous_list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove subreddit list: No list to remove', exc_info=True)
            Message.no_subreddit_list(self)

    def change_subreddit_list(self):
        new_list_name = self.subreddit_list_combo.currentText()
        self.subreddit_list_model.set_list(new_list_name)
        self.subreddit_list_model.sort_list(self.list_sort_method, self.list_order_method)
        self.refresh_subreddit_count()

    def export_subreddit_list_to_text(self):
        current_list = self.subreddit_list_combo.currentText()
        path = SystemUtil.join_path(self.settings_manager.user_save_directory, current_list)
        file_path = self.get_file_path('Export Path', path, 'Text Files (*.txt)')
        if file_path is not None:
            TextExporter.export_reddit_objects_to_text(self.subreddit_list_model.list, file_path)

    def export_subreddit_list_to_json(self):
        current_list = self.subreddit_list_combo.currentText()
        path = SystemUtil.join_path(self.settings_manager.subreddit_save_directory, current_list)
        file_path = self.get_file_path('Export Path', path, 'Json Files (*.json)')
        if file_path is not None:
            JsonExporter.export_reddit_objects_to_json(self.subreddit_list_model.list, file_path)

    def get_file_path(self, suggested_name, ext):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Export Path',
                                                             self.settings_manager.save_directory +
                                                             suggested_name, ext)
    def get_file_path(self, title, suggested_path, ext):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, title, suggested_path, ext)
        return file_path if file_path != '' else None

    def add_user(self):
        if self.user_list_model.list is None:
            self.add_user_list(list_name='Default')
        dialog = AddRedditObjectDialog(self.user_list_model)
        dialog.exec_()

    def remove_user(self):
        """
        Gets the currently selected index from the user list and the current user list model and calls a method to
        remove the object at the current index
        """
        self.remove_reddit_object(self.get_selected_single_user(), self.user_list_model)

    def remove_reddit_object(self, reddit_object, list_model):
        """
        Removes the reddit object at the supplied index from the supplied list_model.
        :param reddit_object: The index of the reddit object to be removed.
        :param list_model: The list model that the reddit object is to be removed from.
        :type reddit_object: RedditObject
        :type list_model: ListModel
        """
        try:
            if Message.remove_reddit_object(self, reddit_object.name):
                list_model.delete_reddit_object(reddit_object)
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
        if Message.reddit_object_not_valid(self, reddit_object.name, reddit_object.object_type):
            self.remove_problem_reddit_object(reddit_object, self.settings_manager.rename_invalidated_download_folders,
                                              'Invalid')

    def remove_forbidden_reddit_object(self, reddit_object):
        """
        Handles removing the supplied reddit object if access to the object is forbidden (ie: a private subreddit).
        This method will not rename the download folder.
        :param reddit_object: The reddit object to which access if forbidden.
        :type reddit_object: RedditObject
        """
        if Message.reddit_object_forbidden(self, reddit_object.name, reddit_object.object_type):
            self.remove_problem_reddit_object(reddit_object, False, 'Forbidden')

    def remove_problem_reddit_object(self, reddit_object, rename, reason):
        """
        Handles the actual removal of the supplied reddit object from the list that it is found in.
        :param reddit_object: The reddit object that is to be removed.
        :param rename: True if the objects download folder is to be renamed.
        :param reason: The reason that the object is being removed.  Used for logging purposes.
        :type reddit_object: RedditObject
        :type rename: bool
        :type reason: str
        """
        working_list = self.get_working_list(reddit_object.object_type)
        working_list.delete_reddit_object(reddit_object)
        rename_message = 'Not Attempted'
        if rename:
            path = self.get_reddit_object_download_folder(reddit_object)
            if not SystemUtil.rename_directory_deleted(path):
                rename_message = 'Failed'
                Message.failed_to_rename_error(self, reddit_object.name)
            else:
                rename_message = 'Success'
        self.refresh_object_count()
        self.logger.info('Invalid reddit object removed', extra={'object_name': reddit_object.name,
                                                                 'folder_rename': rename_message,
                                                                 'removal_reason': reason})

    def get_working_list(self, object_type):
        """
        Returns the list that is currently being displayed based on the supplied object type.
        :param object_type: The type of list that is to be returned.
        :return: The List model that of the supplied object type that is currently being displayed.
        """
        if object_type == 'USER':
            return self.user_list_model
        else:
            return self.subreddit_list_model

    def add_subreddit(self):
        if self.subreddit_list_model.list is None:
            self.add_subreddit_list(list_name='Default')
        add_sub_dialog = AddRedditObjectDialog(self.subreddit_list_model)
        add_sub_dialog.exec_()

    def remove_subreddit(self):
        """
        Gets the currently selected index from the subreddit list and the current subreddit list model and calls a
        method to remove the object at the current index
        """
        self.remove_reddit_object(self.get_selected_single_subreddit(), self.subreddit_list_model)

    def select_directory(self):
        """
        Opens a dialog for the user to select a directory then verifies and returns the selected directory if it exists,
        and returns None if it does not.
        :return: A path to a user selected directory.
        :rtype: str
        """
        folder = str(QFileDialog.getExistingDirectory(self, 'Select The Folder to Import From',
                                                                       self.settings_manager.save_directory))
        if os.path.isdir(folder):
            return folder
        else:
            Message.invalid_file_path(self)
            return None

    def check_existing_object_for_download(self, *existing_names):
        pass

    def check_new_object_for_download(self, reddit_object_id):
        if self.settings_manager.download_on_add:
            self.add_to_download(reddit_object_id)

    def open_download_sessions_dialog(self):
        dialog = DownloadSessionDialog()
        dialog.show()
        dialog.exec_()

    def started_download_gui_shift(self):
        """Disables certain options in the GUI that may be problematic if used while the downloader is running"""
        self.running = True
        self.init_progress_bar()
        self.downloaded = 0
        self.potential_downloads = 0
        self.output_box.clear()
        self.statusbar.clearMessage()
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(True)
        self.shift_download_buttons()

    def finished_download_gui_shift(self):
        """Re-enables disabled GUI options"""
        self.running = False
        self.progress_bar.setVisible(False)
        if len(self.failed_list) > 0:
            self.failed_download_list_menu_item.setEnabled(True)
            if self.settings_manager.auto_display_failed_list:
                self.display_failed_downloads()
        self.potential_downloads = 0
        self.shift_download_buttons()

    def shift_download_buttons(self):
        self.download_button.setVisible(not self.running)
        self.soft_stop_download_button.setVisible(self.running)
        self.terminate_download_button.setVisible(self.running)

    def finish_progress_bar(self):
        """
        Changes the progress bar text to show that it is complete and also moves the progress bar value to the maximum
        if for whatever reason it was not already there
        """
        self.progress_label.setText('Download complete - Downloaded: %s' % self.potential_downloads)
        if self.progress_bar.value() < self.progress_bar.maximum():
            self.progress_bar.setValue(self.progress_bar.maximum())

    def open_settings_dialog(self):
        """Displays the main settings dialog and calls methods that update each reddit object if needed."""
        settings = RedditDownloaderSettingsGUI()
        settings.show()
        dialog = settings.exec_()
        if dialog == QDialog.Accepted:
            self.update_user_settings()
            self.update_subreddit_settings()

    def update_user_settings(self):
        """Iterates through the user list and calls update settings for each user"""
        updated = 0
        total = 0
        with self.db_handler.get_scoped_session() as session:
            for user in session.query(User):
                total += 1
                if not user.lock_settings:
                    self.update_object_settings(user)
                    updated += 1
        self.logger.info('User settings updated', extra={'updated_users': updated, 'total_users': total})

    def update_subreddit_settings(self):
        """Iterates through the subreddit list and calls update settings for each sub"""
        updated = 0
        total = 0
        with self.db_handler.get_scoped_session() as session:
            for subreddit in session.query(Subreddit):
                total += 1
                if not subreddit.lock_settings:
                    self.update_object_settings(subreddit)
                    updated += 1
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
        if dialog == QDialog.Accepted:
            self.settings_manager.auto_display_failed_list = not failed_dialog.auto_display_checkbox.isChecked()

    def set_unfinished_downloads(self, unfinished_list):
        """
        If the downloader is stopped before all content has been downloaded, this will save the list of unfinished
        downloads and enable to file menu button to open the dialog
        """
        self.unfinished_downloads = unfinished_list
        self.unfinished_downloads_available = True
        self.unfinished_downloads_menu_item.setEnabled(True)

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
        ImgurUtils.check_credits()
        reset_time = datetime.strftime(datetime.fromtimestamp(ImgurUtils.credit_reset_time),'%m-%d-%Y at %I:%M %p')
        dialog_text = "Remaining Credits: {}\n" \
                      "Reset Time: {}\n".format(ImgurUtils.num_credits, reset_time)
        if Injector.get_settings_manager().imgur_mashape_key:
            dialog_text += "\nFallback to the commercial API enabled!"
        QMessageBox.information(self, 'Imgur Credits', dialog_text, QMessageBox.Ok)



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
            user_count = self.user_list_model.rowCount()
        except:
            user_count = 0
        self.user_count_label.setText(str(user_count))

    def refresh_subreddit_count(self):
        """Updates the shown subreddit count seen in the list menu"""
        try:
            subreddit_count = self.subreddit_list_model.rowCount()
        except:
            subreddit_count = 0
        self.subreddit_count_label.setText(str(subreddit_count))

    def set_list_sort_method(self, method):
        self.list_sort_method = method
        self.change_list_sort_method()

    def set_list_order_method(self, method):
        self.list_order_method = method
        self.change_list_sort_method()

    def change_list_sort_method(self):
        """Applies the sort and order function to each list model"""
        self.user_list_model.sort_list(self.list_sort_method, self.list_order_method)
        self.subreddit_list_model.sort_list(self.list_sort_method, self.list_order_method)

    def set_view_menu_items_checked(self):
        """A dispatch table to set the correct view menu item checked"""
        pass
        # TODO: fix sorting
        # view_sort_dict = {0: self.sort_list_by_name_menu_item,
        #                   1: self.sort_list_by_date_added_menu_item,
        #                   2: self.sort_list_by_post_count_menu_item}
        # view_order_dict = {0: self.sort_list_ascending_menu_item,
        #                    1: self.sort_list_descending_menu_item}
        # view_sort_dict[self.list_sort_method].setChecked(True)
        # view_order_dict[self.list_order_method].setChecked(True)

    def closeEvent(self, QCloseEvent):
        self.close()

    def close_from_menu(self):
        self.close()

    def close(self):
        self.receiver.stop_run()
        self.save_main_window_settings()
        self.settings_manager.save_all()
        super().close()

    def save_main_window_settings(self):
        self.settings_manager.main_window_geom['width'] = self.width()
        self.settings_manager.main_window_geom['height'] = self.height()
        self.settings_manager.main_window_geom['x'] = self.x()
        self.settings_manager.main_window_geom['y'] = self.y()
        self.settings_manager.horizontal_splitter_state = self.horz_splitter.sizes()
        self.settings_manager.list_sort_method = self.list_sort_method
        self.settings_manager.list_order_method = self.list_order_method
        self.settings_manager.current_user_list = self.user_lists_combo.currentText()
        self.settings_manager.current_subreddit_list = self.subreddit_list_combo.currentText()

        if self.download_users_radio.isChecked():
            self.settings_manager.download_radio_state = 'USER'
        elif self.download_subreddits_radio.isChecked():
            self.settings_manager.download_radio_state = 'SUBREDDIT'
        else:
            self.settings_manager.download_radio_state = 'CONSTRAIN'

    def load_state(self):
        """
        Loads the last used user and subreddit lists from the database.  Handled here in its own method so that any
        problems with loading can be logged.
        """
        with self.db_handler.get_scoped_session() as session:
            self.load_list_combos(session)
            self.load_user_list(session)
            self.load_subreddit_list(session)

    def load_list_combos(self, session):
        user_lists = [x.name for x in session.query(RedditObjectList).filter(RedditObjectList.list_type == 'USER')]
        sub_lists = \
            [x.name for x in session.query(RedditObjectList).filter(RedditObjectList.list_type == 'SUBREDDIT')]
        self.user_lists_combo.addItems(user_lists)
        self.subreddit_list_combo.addItems(sub_lists)

    def load_user_list(self, session):
        try:
            list_name = self.settings_manager.current_user_list
            if list_name == '':
                row = session.query(RedditObjectList.name).filter(RedditObjectList.list_type == 'USER').first()
                if row is not None:
                    list_name = row.name
            if list_name != '':
                self.user_list_model.set_list(list_name)
                self.user_lists_combo.setCurrentText(list_name)
        except:
            self.logger.error('Failed to load user list from database', exc_info=True)

    def load_subreddit_list(self, session):
        try:
            list_name = self.settings_manager.current_subreddit_list
            if list_name == '':
                row = session.query(RedditObjectList.name)\
                    .filter(RedditObjectList.list_type == 'SUBREDDIT').first()
                if row is not None:
                    list_name = row.name
            if list_name != '':
                self.subreddit_list_model.set_list(list_name)
                self.subreddit_list_combo.setCurrentText(list_name)
        except:
            self.logger.error('Failed to load subreddit list from database', exc_info=True)

    def open_data_directory(self):
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
        self.update_thread = QThread()
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

    def display_ffmpeg_info_dialog(self):
        dialog = FfmpegInfoDialog()
        dialog.exec_()

    def check_ffmpeg(self):
        """
        Checks that ffmpeg is installed on the host system and notifies the user if it is not installed.  Will also
        disable reddit video download depending on the user input through the dialog.
        """
        if not VideoMerger.ffmpeg_valid and self.settings_manager.display_ffmpeg_warning_dialog:
            disable = Message.ffmpeg_warning(self)
            self.settings_manager.download_reddit_hosted_videos = not disable
            self.settings_manager.display_ffmpeg_warning_dialog = False
