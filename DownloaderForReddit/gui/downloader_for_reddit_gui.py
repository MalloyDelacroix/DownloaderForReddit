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


import io
import platform
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QActionGroup, QAbstractItemView, QProgressBar, QLabel, QMenu, QInputDialog,
                             QMessageBox, QWidget, QHBoxLayout, QSystemTrayIcon, QApplication)
from PyQt5.QtCore import QThread, Qt, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices, QPixmap, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtNetworkAuth import QOAuth2AuthorizationCodeFlow, QOAuthHttpServerReplyHandler
from pyqtspinner.spinner import WaitingSpinner
import logging

from ..guiresources.downloader_for_reddit_gui_auto import Ui_MainWindow
from ..gui.about_dialog import AboutDialog
from ..gui.add_reddit_object_dialog import AddRedditObjectDialog
from ..gui.existing_reddit_object_add_dialog import ExistingRedditObjectAddDialog
from ..gui.ffmpeg_info_dialog import FfmpegInfoDialog
from ..gui import message_dialogs
from ..gui.reddit_object_settings_dialog import RedditObjectSettingsDialog
from ..gui.update_dialog_gui import UpdateDialog
from ..gui.database_views.database_dialog import DatabaseDialog
from ..gui.database_views.database_statistics_dialog import DatabaseStatisticsDialog
from ..gui.settings.settings_dialog import SettingsDialog
from ..gui.export_wizard import ExportWizard
from ..gui.invalid_reddit_object_dialog import InvalidRedditObjectDialog, InvalidObject
from ..core.download_runner import DownloadRunner
from ..core.update_runner import UpdateRunner
from ..core.cli import CLI
from ..database.models import RedditObject, RedditObjectList, ListAssociation
from ..database.filters import RedditObjectFilter
from ..database.model_manager import ModelManger
from ..utils import (injector, system_util, imgur_utils, video_merger, general_utils, UpdateChecker, reddit_utils)
from ..viewmodels.reddit_object_list_model import RedditObjectListModel
from ..viewmodels.output_view_model import OutputViewModel
from ..messaging.message import MessageType, MessagePriority, Message
from ..version import __version__


class DownloaderForRedditGUI(QMainWindow, Ui_MainWindow):

    stop_download_signal = pyqtSignal(bool)  # bool indicates whether the stop is a hard stop or not

    def __init__(self, queue, receiver, scheduler):
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
        self.invalid_list = []
        self.db_handler = injector.get_database_handler()
        self.spinner = WaitingSpinner(self.user_list_view, roundness=80.0, opacity=10.0, fade=72.0, radius=10.0,
                                      lines=12, line_length=12.0, line_width=4.0, speed=1.4, color=(0, 0, 0))
        self.tray_icon_image = \
            QIcon(QPixmap('Resources/Images/RedditDownloaderIcon.png').scaled(48, 48))
        self.system_tray_icon = QSystemTrayIcon(icon=self.tray_icon_image)
        self.oauth = None

        # region Settings
        self.settings_manager = injector.get_settings_manager()

        geom = self.settings_manager.main_window_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.horz_splitter.setSizes(self.settings_manager.horizontal_splitter_state)

        if self.settings_manager.download_radio_state == 'USER':
            self.download_users_radio.setChecked(True)
        elif self.settings_manager.download_radio_state == 'SUBREDDIT':
            self.download_subreddits_radio.setChecked(True)
        else:
            self.constain_to_sub_list_radio.setChecked(True)
        # endregion

        self.queue = queue
        self.receiver = receiver
        self.scheduler = scheduler

        self.output_view_model = OutputViewModel()
        self.output_list_view.setModel(self.output_view_model)
        self.output_view_model.added.connect(self.scroll_output)

        reddit_utils.load_token()
        user = reddit_utils.check_authorized_connection()

        if user is not None:
            Message.send_info(f'You are logged in as /u/{user}.')
        else:
            Message.send_info('You are not logged in to Reddit.')
        # region Main Menu

        # region File Menu
        self.open_settings_menu_item.triggered.connect(self.open_settings_dialog)
        if user:
            self.connect_reddit_account_menu_item.setText(f"Sign out: {user}")
            self.connect_reddit_account_menu_item.triggered.connect(self.sign_out)
        else:
            self.connect_reddit_account_menu_item.setText(f"Connect Reddit Account")
            self.connect_reddit_account_menu_item.triggered.connect(self.start_oauth_flow)
        self.open_data_directory_menu_item.triggered.connect(self.open_data_directory)
        self.minimize_to_tray_menu_item.triggered.connect(self.minimize_to_tray)
        self.exit_menu_item.triggered.connect(self.close)
        # endregion

        # region View Menu
        self.setup_list_sort_menu()

        self.list_view_order_group = QActionGroup(self)
        self.list_view_order_group.addAction(self.sort_list_ascending_menu_item)
        self.list_view_order_group.addAction(self.sort_list_descending_menu_item)
        self.sort_list_ascending_menu_item.triggered.connect(lambda: self.set_list_order(desc=False))
        self.sort_list_descending_menu_item.triggered.connect(lambda: self.set_list_order(desc=True))
        self.sort_list_ascending_menu_item.setChecked(not self.settings_manager.order_list_desc)
        self.sort_list_descending_menu_item.setChecked(self.settings_manager.order_list_desc)
        # endregion

        # region Lists Menu
        self.add_user_list_menu_item.triggered.connect(self.add_user_list)
        self.remove_user_list_menu_item.triggered.connect(self.remove_user_list)
        self.add_subreddit_list_menu_item.triggered.connect(self.add_subreddit_list)
        self.remove_subreddit_list_menu_item.triggered.connect(self.remove_subreddit_list)

        self.export_user_list_menu_item.triggered.connect(self.export_user_list)
        self.export_subreddit_list_menu_item.triggered.connect(self.export_subreddit_list)
        # endregion

        # region Database Menu
        self.database_view_menu_item.triggered.connect(self.open_database_view_dialog)
        self.download_sessions_view_menu_item.triggered.connect(self.open_download_sessions_dialog)
        self.reddit_objects_view_menu_item.triggered.connect(self.open_reddit_objects_dialog)
        self.posts_view_menu_item.triggered.connect(self.open_posts_dialog)
        self.content_view_menu_item.triggered.connect(self.open_content_dialog)
        self.comments_view_menu_item.triggered.connect(self.open_comment_dialog)
        self.failed_extraction_view_menu_item.triggered.connect(self.open_failed_extraction_dialog)
        self.failed_download_view_menu_item.triggered.connect(self.open_failed_downloads_dialog)
        self.statistics_view_menu_item.triggered.connect(self.open_database_statistics_dialog)
        # endregion

        # region Download Menu
        self.download_user_list_menu_item.triggered.connect(self.download_user_list)
        self.download_subreddit_list_menu_item.triggered.connect(self.download_subreddit_list)
        self.download_user_list_constrained_menu_item.triggered.connect(self.download_user_list_constrained)
        self.run_unfinished_extractions_menu_item.triggered.connect(self.run_unextracted_only)
        self.run_unfinished_downloads_menu_item.triggered.connect(self.run_undownloaded_only)
        self.run_all_unfiinished_menu_item.triggered.connect(self.run_all_unfinished)
        # endregion

        # region Help Menu
        self.imgur_credit_dialog_menu_item.triggered.connect(self.display_imgur_client_information)
        self.user_manual_menu_item.triggered.connect(self.open_user_manual)
        self.user_manual_menu_item.setDisabled(True)  # TODO: enable after online user manual is created
        self.ffmpeg_requirement_dialog_menu_item.triggered.connect(self.display_ffmpeg_info_dialog)
        self.command_line_options_menu_item.triggered.connect(self.output_command_line_options)
        self.check_for_updates_menu_item.triggered.connect(lambda: self.check_for_updates(True))
        self.about_menu_item.triggered.connect(self.display_about_dialog)
        # endregion

        # endregion

        self.user_list_model = RedditObjectListModel('USER')
        self.user_list_model.starting_add.connect(self.start_spinner)
        self.user_list_model.finished_add.connect(self.stop_spinner)
        self.user_list_model.reddit_object_added.connect(self.check_new_object_for_download)
        self.user_list_model.existing_object_added.connect(self.check_existing_object_for_download)
        self.user_list_model.new_object_in_list.connect(lambda x: self.scroll_to_new(x, 'USER'))
        self.user_list_model.count_change.connect(lambda x: self.user_count_label.setText(str(x)))
        self.user_list_view.setModel(self.user_list_model)
        self.subreddit_list_model = RedditObjectListModel('SUBREDDIT')
        self.subreddit_list_model.starting_add.connect(self.start_spinner)
        self.subreddit_list_model.finished_add.connect(self.stop_spinner)
        self.subreddit_list_model.reddit_object_added.connect(self.check_new_object_for_download)
        self.subreddit_list_model.existing_object_added.connect(self.check_existing_object_for_download)
        self.subreddit_list_model.new_object_in_list.connect(lambda x: self.scroll_to_new(x, 'SUBREDDIT'))
        self.subreddit_list_model.count_change.connect(lambda x: self.subreddit_count_label.setText(str(x)))
        self.subreddit_list_view.setModel(self.subreddit_list_model)

        self.load_state()

        self.user_list_search_edit.textChanged.connect(
            lambda text: self.user_list_model.search_list(text))
        self.subreddit_list_search_edit.textChanged.connect(
            lambda text: self.subreddit_list_model.search_list(text))

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

        self.user_list_view.doubleClicked.connect(lambda: self.user_settings(self.get_selected_users()))
        self.user_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.user_lists_combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_lists_combo.customContextMenuRequested.connect(self.user_list_combo_context_menu)

        self.subreddit_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subreddit_list_view.customContextMenuRequested.connect(
            lambda: self.reddit_object_list_context_menu('SUBREDDIT'))

        self.subreddit_list_view.doubleClicked.connect(
            lambda: self.subreddit_settings(self.get_selected_subreddits()))
        self.subreddit_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.subreddit_list_combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subreddit_list_combo.customContextMenuRequested.connect(self.subreddit_list_combo_context_menu)

        self.schedule_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.schedule_widget.customContextMenuRequested.connect(self.schedule_context_menu)

        self.output_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.output_list_view.customContextMenuRequested.connect(self.output_context_menu)

        self.run_time = 0
        self.timer_widget = QWidget()
        self.timer_widget.setVisible(False)
        layout = QHBoxLayout()
        layout.setContentsMargins(11, 0, 11, 0)
        self.timer_widget.setLayout(layout)
        self.perpetual_run_label = QLabel('Perpetual Run |')
        layout.addWidget(self.perpetual_run_label)
        layout.addWidget(QLabel('Run Time: '))
        self.timer_label = QLabel('00:00:00')
        layout.addWidget(self.timer_label)

        self.statusbar.addPermanentWidget(self.timer_widget)
        self.run_timer = QTimer(self)
        self.run_timer.timeout.connect(self.update_run_time)

        self.progress_bar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.statusbar.addPermanentWidget(self.progress_label)
        self.progress_label.setText('Extraction Complete')
        self.progress_label.setVisible(False)

        self.setup_system_tray_icon()

        self.check_ffmpeg()
        self.check_for_updates(False)


        self.log_startup()

    def log_startup(self):
        self.logger.info('Application started', extra={
            'dfr_version': __version__,
            'platform': platform.platform(),
            'account_connected': reddit_utils.connection_is_authorized,
        })

    def setup_list_sort_menu(self):
        list_view_group = QActionGroup(self)
        for field in RedditObjectFilter.get_order_fields():
            text = field.replace('_', ' ').title()
            item = self.list_sort_menu_item.addAction(text, lambda value=field: self.set_list_order(order_by=value))
            list_view_group.addAction(item)
            item.setCheckable(True)
            item.setChecked(field == self.settings_manager.list_order_method)

    def scroll_output(self):
        """
        Scrolls the output to the bottom when a new output message is added and the scroll bar position is in the lower
        5th percentile of the view.
        """
        try:
            bar = self.output_list_view.verticalScrollBar()
            pos = bar.value()
            max_ = bar.maximum()
            if pos == max_ or ((pos / max_) * 100) >= 96:
                self.output_list_view.scrollToBottom()
        except ZeroDivisionError:
            pass

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

    # region Context Menus
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
        export_text = f'Export {ros[0].name}' if len(ros) == 1 else f'Export {len(ros)} {object_type.title()}s'
        export = menu.addAction(export_text, lambda: self.export_reddit_objects(ros))
        menu.addSeparator()
        open_post_dialog = menu.addAction('Post View',
                                             lambda: self.open_selected_reddit_object_dialog(ros[0].id, 'POST'))
        open_content_dialog = menu.addAction('Content View',
                                             lambda: self.open_selected_reddit_object_dialog(ros[0].id, 'CONTENT'))
        menu.addSeparator()
        add_object = menu.addAction(f'Add {object_type.title()}', add_command)
        remove_text = f'Remove {ros[0].name}' if len(ros) == 1 else f'Remove {len(ros)} {object_type.title()}s'
        remove_object = menu.addAction(remove_text, remove_command)
        menu.addSeparator()
        self.move_reddit_object_menu_item(menu, ros, object_type, 'MOVE')
        self.move_reddit_object_menu_item(menu, ros, object_type, 'COPY')
        menu.addSeparator()
        delete_menu = menu.addMenu(f'Delete {object_type.title()}')
        delete_menu.addAction(f'Delete {object_type.title()}',
                              lambda: self.delete_reddit_objects(ros, delete_files=False))
        delete_menu.addAction(f'Delete {object_type.title()} with Files',
                              lambda: self.delete_reddit_objects(ros, delete_files=True))
        menu.addSeparator()
        disable_enable_download_option = True
        if all(x.download_enabled == enabled for x in ros):
            enabled_text = 'Enable Download' if not enabled else 'Disable Download'
            if len(ros) > 0:
                disable_enable_download_option = False
        else:
            enabled_text = 'Differing Download Enabled States'
        enable_download = menu.addAction(enabled_text, lambda: [ro.toggle_enable_download() for ro in ros])
        download = menu.addAction(download_text, lambda: self.add_to_download(*[x.id for x in ros]))

        for action in menu.actions():
            if action != add_object:
                action.setDisabled(len(ros) <= 0)
        enable_download.setDisabled(disable_enable_download_option)

        menu.exec_(QCursor.pos())

    def move_reddit_object_menu_item(self, main_menu, reddit_objects, ro_type, action_type):
        try:
            if len(reddit_objects) > 1:
                text = f'{action_type.title()} {len(reddit_objects)} {ro_type.lower()}s to:'
            else:
                text = f'{action_type.title()} {reddit_objects[0].name if len(reddit_objects) else ""} to:'
            menu = main_menu.addMenu(text)
            current_list_model = self.user_list_model if ro_type == 'USER' else self.subreddit_list_model
            current_list_id = current_list_model.list.id  # Throws attribute error when no list is available
            with self.db_handler.get_scoped_session() as session:
                lists = session.query(RedditObjectList) \
                    .filter(RedditObjectList.list_type == ro_type) \
                    .filter(RedditObjectList.id != current_list_id)
            action = self.move_reddit_objects if action_type == 'MOVE' else self.copy_reddit_objects
            for ro_list in lists:
                menu.addAction(
                    ro_list.name,
                    lambda new_list=ro_list: action([x.id for x in reddit_objects], current_list_id, new_list.id))
            return menu
        except AttributeError:
            # In this case there is no available list
            return None

    def move_reddit_objects(self, reddit_object_ids, old_list_id, new_list_id):
        if self.settings_manager.ask_to_sync_moved_ro_settings:
            text = 'Would you like to sync the settings of the moved user/subreddit(s) to the settings defined for ' \
                   'the list they are being moved to?'
            sync, ask = message_dialogs.optional_question_dialog(self, 'Sync Settings?', text,
                                                                 checkbox_text='Do not ask again')
            self.settings_manager.ask_to_sync_moved_ro_settings = not ask
        else:
            sync = True
        with self.db_handler.get_scoped_update_session() as session:
            for ro_id in reddit_object_ids:
                session.query(ListAssociation)\
                    .filter(ListAssociation.reddit_object_id == ro_id)\
                    .filter(ListAssociation.reddit_object_list_id == old_list_id).delete()
                new_assoc = ListAssociation(reddit_object_id=ro_id, reddit_object_list_id=new_list_id)
                session.add(new_assoc)
                if sync:
                    new_list = session.query(RedditObjectList).get(new_list_id)
                    reddit_object = session.query(RedditObject).get(ro_id)
                    new_list.sync_reddit_object_settings(reddit_object)
        self.refresh_list_models()

    def copy_reddit_objects(self, reddit_object_ids, old_list_model, new_list_id):
        with self.db_handler.get_scoped_update_session() as session:
            for ro_id in reddit_object_ids:
                new_assoc = ListAssociation(reddit_object_id=ro_id, reddit_object_list_id=new_list_id)
                session.add(new_assoc)

    def user_list_combo_context_menu(self):
        menu = QMenu()
        menu.addAction('Add User List', self.add_user_list)
        remove = menu.addAction('Remove User List', self.remove_user_list)
        remove.setDisabled(self.user_lists_combo.currentText() == '')
        menu.addSeparator()
        settings = menu.addAction('List Settings', self.user_list_settings)
        settings.setDisabled(self.user_lists_combo.currentText() == '')
        menu.exec_(QCursor.pos())

    def subreddit_list_combo_context_menu(self):
        menu = QMenu()
        menu.addAction('Add Subreddit List', self.add_subreddit_list)
        remove = menu.addAction('Remove Subreddit List', self.remove_subreddit_list)
        remove.setDisabled(self.subreddit_list_combo.currentText() == '')
        menu.addSeparator()
        settings = menu.addAction('List Settings', self.subreddit_list_settings)
        settings.setDisabled(self.subreddit_list_combo.currentText() == '')
        menu.exec_(QCursor.pos())

    def refresh_list_models(self):
        """
        Refreshes the user and subreddit lists from the database.  Should be called after settings changes to lists are
        made in other parts of the application.
        """
        self.user_list_model.refresh_session()
        self.subreddit_list_model.refresh_session()

    def schedule_context_menu(self):
        menu = QMenu()
        menu.addAction('Schedule Settings', lambda: self.open_settings_dialog(open_display='Schedule'))
        menu.exec_(QCursor.pos())

    def output_context_menu(self):
        menu = QMenu()
        menu.addAction('Output Settings', lambda: self.open_settings_dialog(open_display='Output'))
        menu.addSeparator()
        menu.addAction('Clear Output', lambda: self.output_view_model.clear())
        menu.exec_(QCursor.pos())
    # endregion

    def user_settings(self, users):
        """
        Opens the RedditObjectSettingsDialog and sets the supplied user as the selected user to display the settings
        for.  The current user list is also taken by the dialog and the names shown in the additional objects list.
        :param users: A list of users that is to be set as the currently selected users list in the settings dialog.
        """
        if users is None:
            users = [self.user_list_model.reddit_objects[0]]
        id_list = [x.id for x in users]
        dialog = RedditObjectSettingsDialog('USER', self.user_list_model.list.name, selected_object_ids=id_list,
                                            parent=self)
        dialog.download_signal.connect(lambda download_ids: self.add_to_download(*download_ids))
        dialog.show()
        dialog.exec_()

    def subreddit_settings(self, subreddits):
        """Operates the same as the user_settings function"""
        if subreddits is None:
            subreddits = [self.subreddit_list_model.reddit_objects[0]]
        id_list = [x.id for x in subreddits]
        dialog = RedditObjectSettingsDialog('SUBREDDIT', self.subreddit_list_model.list.name,
                                            selected_object_ids=id_list, parent=self)
        dialog.download_signal.connect(lambda download_ids: self.add_to_download(*download_ids))
        dialog.show()
        dialog.exec_()

    def user_list_settings(self):
        try:
            self.open_settings_dialog(open_display='Download Defaults', open_list_id=self.user_list_model.list.id)
        except AttributeError:
            pass

    def subreddit_list_settings(self):
        try:
            self.open_settings_dialog(open_display='Download Defaults', open_list_id=self.subreddit_list_model.list.id)
        except AttributeError:
            pass

    def open_reddit_object_download_folder(self, reddit_object: RedditObject):
        general_utils.open_reddit_object_download_folder(reddit_object, self)

    def run_full_download(self):
        run_unextracted = self.settings_manager.finish_incomplete_extractions_at_session_start
        run_undownloaded = self.settings_manager.finish_incomplete_downloads_at_session_start
        kwargs = {
            'run_unextracted': run_unextracted,
            'run_undownloaded': run_undownloaded
        }
        if self.download_users_radio.isChecked():
            self.download_user_list(**kwargs)
        elif self.download_subreddits_radio.isChecked():
            self.download_subreddit_list(**kwargs)
        else:
            self.download_user_list_constrained(**kwargs)

    def download_user_list(self, **kwargs):
        user_id_list = self.user_list_model.get_id_list()
        self.run(user_id_list, None, **kwargs)

    def download_subreddit_list(self, **kwargs):
        sub_id_list = self.subreddit_list_model.get_id_list()
        self.run(None, sub_id_list, **kwargs)

    def download_user_list_constrained(self, **kwargs):
        user_id_list = self.user_list_model.get_id_list()
        sub_id_list = self.subreddit_list_model.get_id_list()
        self.run(user_id_list, sub_id_list, **kwargs)

    def run_all_unfinished(self, *, post_id_list=None, content_id_list=None):
        self.run(None, None, run_new=False, run_unextracted=True, run_undownloaded=True,
                 unextracted_id_list=post_id_list, undownloaded_id_list=content_id_list)

    def run_unextracted_only(self, *, id_list=None):
        self.run(None, None, run_new=False, run_unextracted=True, unextracted_id_list=id_list)

    def run_undownloaded_only(self, *, id_list=None):
        self.run(None, None, run_new=False, run_undownloaded=True, undownloaded_id_list=id_list)

    def run_scheduled_download(self, id_tuple):
        if not self.running:
            user_list_id, subreddit_list_id = id_tuple
            user_id_list = None
            sub_id_list = None
            run_unextracted = self.settings_manager.finish_incomplete_extractions_at_session_start
            run_undownloaded = self.settings_manager.finish_incomplete_downloads_at_session_start
            with self.db_handler.get_scoped_session() as session:
                if user_list_id is not None:
                    user_id_list = session.query(RedditObjectList).get(user_list_id).get_reddit_object_id_list()
                if subreddit_list_id is not None:
                    sub_id_list = session.query(RedditObjectList).get(subreddit_list_id).get_reddit_object_id_list()
                self.run(user_id_list, sub_id_list, run_unextracted=run_unextracted, run_undownloaded=run_undownloaded)

    def run(self, user_id_list, sub_id_list, reddit_object_id_list=None, **kwargs):
        self.started_download_gui_shift()

        self.download_runner = DownloadRunner(
            user_id_list=user_id_list,
            subreddit_id_list=sub_id_list,
            reddit_object_id_list=reddit_object_id_list,
            **kwargs
        )

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

    def update_post_scores(self, post_id_list):
        post_count = len(post_id_list)
        if post_count < 200 or self.large_post_update_alert(post_count):
            self.update_runner = UpdateRunner(run_method='UPDATE_SCORES', post_id_list=post_id_list)
            self.run_update(self.update_runner)

    def fetch_new_post_comments(self, post_id_list):
        post_count = len(post_id_list)
        if post_count < 200 or self.large_post_update_alert(post_count):
            self.update_runner = UpdateRunner(run_method='UPDATE_COMMENTS', post_id_list=post_id_list)
            self.run_update(self.update_runner)

    def large_post_update_alert(self, count):
        """
        Alerts the user when a large number of posts are about to be updated and asks if they want to proceed.  The
        answer to that question is returned.  The settings manager is checked before displaying the dialog to see if
        the ignore flag for this dialog is set.  If it is set to be ignored, True is always returned.
        :param count: The number of posts that are about to be updated.  Supplied so it can be displayed to the user.
        :return: True if the update action should proceed, False if it should not.
        """
        if self.settings_manager.large_post_update_warning:
            accepted, do_not_show = message_dialogs.optional_question_dialog(
                self, 'Update Posts?', f'There are {"{:,}".format(count)} posts in this selection to be updated.  It '
                                       f'could take a while to update this many posts.\n\n'
                                       f'Are you sure you want to proceed?')
            self.settings_manager.large_post_update_warning = not do_not_show
            return accepted
        else:
            return True

    def run_update(self, update_runner):
        self.update_check_thread = QThread()
        update_runner.moveToThread(self.update_check_thread)
        self.stop_download_signal.connect(update_runner.stop)
        update_runner.finished.connect(self.update_check_thread.quit)
        update_runner.finished.connect(self.update_runner.deleteLater)
        self.update_check_thread.finished.connect(self.update_check_thread.deleteLater)
        self.update_check_thread.finished.connect(self.finish_update)
        self.update_check_thread.started.connect(update_runner.run)
        self.update_check_thread.start()

    def finish_update(self):
        pass

    def handle_message(self, message):
        if message.message_type == MessageType.STATUS_TRAY:
            self.set_tray_icon_message(message)
        else:
            self.output_view_model.handle_message(message)

    def handle_progress(self, message):
        """
        Handles non-text style messages that it receives from the message receiver.  Decides what to update on the main
        window based on the type of message received as well as the priority of that message.
        :param message: The message sent from some part of the application to update the main window UI.
        """
        if message.message_type == MessageType.POTENTIAL_PROGRESS:
            if message.priority != MessagePriority.ERROR:
                self.extend_progress()
            else:
                self.extend_progress(forward=False)
        elif message.message_type == MessageType.ACTUAL_PROGRESS:
            self.update_progress()
        elif message.message_type == MessageType.POTENTIAL_COUNT:
            if message.priority != MessagePriority.ERROR:
                self.extend_progress()
                self.potential_downloads += 1
                self.update_status_bar()
            else:
                self.extend_progress(forward=False)
                self.potential_downloads -= 1
                self.update_status_bar()
        else:
            self.update_progress()
            self.downloaded += 1
            self.update_status_bar()

    def start_main_spinner(self):
        self.spinner.setParent(self)
        self.spinner.start()

    def start_spinner(self, list_model):
        if list_model == self.user_list_model:
            parent = self.user_list_view
        else:
            parent = self.subreddit_list_view
        self.spinner.setParent(parent)
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()

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

    def update_scheduled_download(self, countdown):
        if countdown is not None and self.settings_manager.show_schedule_countdown != 'DO_NOT_SHOW':
            self.schedule_widget.setVisible(True)
            self.schedule_label.setText(countdown)
        else:
            self.schedule_label.setText('No Download Scheduled')
            if self.settings_manager.show_schedule_countdown != 'SHOW':
                self.schedule_widget.setVisible(False)

    def add_user_list(self, *, list_name=None):
        if list_name is None:
            list_name = self.get_list_name('USER')
        if list_name is not None:
            if list_name != '':
                added = self.user_list_model.add_new_list(list_name, 'USER')
                if added:
                    self.user_lists_combo.addItem(list_name)
                    self.user_lists_combo.setCurrentText(list_name)
                else:
                    text = f'A user list already exists with the name "{list_name}"'
                    message_dialogs.generic_message(self, title='List Name Exists', text=text)
            else:
                self.logger.warning('Unable to add user list', extra={'invalid_name': list_name}, exc_info=True)
                message_dialogs.not_valid_name(self)

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
            if self.verify_remove_list('user'):
                current_user_list = self.user_lists_combo.currentText()
                list_size = self.user_list_model.rowCount()
                self.user_list_model.delete_current_list()
                self.user_lists_combo.removeItem(self.user_lists_combo.currentIndex())
                if self.user_lists_combo.currentText() != '':
                    self.user_list_model.set_list(self.user_lists_combo.currentText())
                    self.user_list_model.sort_list()
                self.logger.info('User list removed', extra={'list_name': current_user_list,
                                                             'previous_list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove user list: No user list available to remove', exc_info=True)
            message_dialogs.no_user_list(self)

    def change_user_list(self):
        """Changes the user list model based on the user_list_combo"""
        new_list_name = self.user_lists_combo.currentText()
        self.user_list_model.set_list(new_list_name)
        self.user_list_model.sort_list()
        self.logger.info('User list changed to: %s' % new_list_name)

    def export_user_list(self):
        wizard = ExportWizard(self.user_list_model.list, RedditObjectList, self.user_list_model.name, parent=self)
        wizard.exec_()

    def export_reddit_objects(self, ro_list):
        wizard = ExportWizard(ro_list, RedditObject, None, parent=self)
        wizard.exec_()

    def add_subreddit_list(self, *, list_name=None):
        if list_name is None:
            list_name = self.get_list_name('SUBREDDIT')
        if list_name is not None:
            if list_name != '':
                added = self.subreddit_list_model.add_new_list(list_name, 'SUBREDDIT')
                if added:
                    self.subreddit_list_combo.addItem(list_name)
                    self.subreddit_list_combo.setCurrentText(list_name)
                else:
                    text = f'A subreddit list already exists with the name "{list_name}"'
                    message_dialogs.generic_message(self, title='List Name Exists', text=text)
            else:
                self.logger.warning('Unable to add subreddit list', extra={'invalid_name': list_name},
                                    exc_info=True)
                message_dialogs.not_valid_name(self)

    def remove_subreddit_list(self):
        try:
            if self.verify_remove_list('subreddit'):
                current_sub_list = self.subreddit_list_combo.currentText()
                list_size = self.subreddit_list_model.rowCount()
                self.subreddit_list_model.delete_current_list()
                self.subreddit_list_combo.removeItem(self.subreddit_list_combo.currentIndex())
                if self.subreddit_list_combo.currentText() != '':
                    self.subreddit_list_model.set_list(self.subreddit_list_combo.currentText())
                    self.subreddit_list_model.sort_list()
                self.logger.info('Subreddit list removed', extra={'list_name': current_sub_list,
                                                                  'previous_list_size': list_size})
        except KeyError:
            self.logger.warning('Unable to remove subreddit list: No list to remove', exc_info=True)
            message_dialogs.no_subreddit_list(self)

    def verify_remove_list(self, list_type):
        """
        Checks the settings manager to see if the user should be asked before removing a reddit object list.  If the
        user should not be asked, True is returned.  Otherwise the users answer is returned.
        :param list_type: The type of list that is to be removed.
        :return: True if the list should be removed, False if not.
        """
        if self.settings_manager.remove_reddit_object_list_warning:
            remove, warn = message_dialogs.remove_list(self, list_type)
            self.settings_manager.remove_reddit_object_list_warning = not warn
            return remove
        else:
            return True

    def change_subreddit_list(self):
        new_list_name = self.subreddit_list_combo.currentText()
        self.subreddit_list_model.set_list(new_list_name)
        self.subreddit_list_model.sort_list()

    def export_subreddit_list(self):
        wizard = ExportWizard(self.subreddit_list_model.reddit_objects, RedditObjectList,
                              self.subreddit_list_model.name, parent=self)
        wizard.exec_()

    def add_user(self):
        if self.user_list_model.list is None:
            self.add_user_list(list_name='Default')
        dialog = AddRedditObjectDialog(self.user_list_model, self)
        dialog.exec_()

    def remove_user(self):
        """
        Gets the currently selected index from the user list and the current user list model and calls a method to
        remove the object at the current index
        """
        self.remove_reddit_object(self.get_selected_users(), self.user_list_model)

    def remove_reddit_object(self, reddit_objects, list_model):
        """
        Removes the supplied reddit object from the supplied list_model.
        :param reddit_objects: A list of reddit objects to be removed.
        :param list_model: The list model that the reddit object is to be removed from.
        :type reddit_objects: list
        :type list_model: ListModel
        """
        try:
            remove = True
            if self.settings_manager.remove_reddit_object_warning:
                remove, warn = message_dialogs.remove_reddit_objects(self, reddit_objects)
                self.settings_manager.remove_reddit_object_warning = not warn
            if remove:
                list_model.remove_reddit_objects(*reddit_objects)
        except (KeyError, AttributeError):
            self.logger.warning('Remove reddit object failed: No object selected', exc_info=True)
            message_dialogs.no_reddit_object_selected(self, list_model.list_type)

    def remove_invalid_reddit_object(self, reddit_object_id):
        """
        Handles removing the supplied reddit object if the downloader finds that the reddit object is not valid.  This
        method also renames the download folder.
        :param reddit_object_id: The id of the reddit object (User or Subreddit) that is invalid and is to be removed.
        :type reddit_object_id: int
        """
        with self.db_handler.get_scoped_update_session() as session:
            reddit_object = session.query(RedditObject).get(reddit_object_id)
            self.invalid_list.append(InvalidObject(reddit_object.name, reddit_object.id, 'deleted'))

    def remove_forbidden_reddit_object(self, reddit_object_id):
        """
        Handles removing the supplied reddit object if access to the object is forbidden (ie: a private subreddit).
        This method will not rename the download folder.
        :param reddit_object_id: The id of the reddit object to which access if forbidden.
        :type reddit_object_id: int
        """
        with self.db_handler.get_scoped_update_session() as session:
            reddit_object = session.query(RedditObject).get(reddit_object_id)
            self.invalid_list.append(InvalidObject(reddit_object.name, reddit_object.id, 'suspended/banned'))

    def remove_problem_reddit_object(self, reddit_object_id, rename, reason):
        """
        Handles the actual removal of the supplied reddit object from the list that it is found in.
        :param reddit_object_id: The id of the reddit object that is to be removed.
        :param rename: True if the objects download folder is to be renamed.
        :param reason: The reason that the object is being removed.  Used for logging purposes.
        :type reddit_object_id: int
        :type rename: bool
        :type reason: str
        """
        with self.db_handler.get_scoped_update_session() as session:
            reddit_object = session.query(RedditObject).get(reddit_object_id)
            session.query(ListAssociation).filter(ListAssociation.reddit_object_id == reddit_object_id).delete()
            rename_message = 'Not Attempted'
            if rename:
                path = general_utils.get_reddit_object_download_folder(reddit_object)
                if not general_utils.rename_invalid_directory(path):
                    rename_message = 'Failed'
                    message_dialogs.failed_to_rename_error(self, reddit_object.name)
                else:
                    rename_message = 'Success'
            self.logger.info('Invalid reddit object removed', extra={'object_name': reddit_object.name,
                                                                     'folder_rename': rename_message,
                                                                     'removal_reason': reason})
        self.refresh_list_models()

    def delete_reddit_objects(self, reddit_objects, delete_files):
        count_text = \
            f'{len(reddit_objects)} {reddit_objects[0].object_type.lower()}{"s" if len(reddit_objects) > 1 else ""}'
        text = f'Are you sure you want to permanently delete {count_text} from the database?\n' \
               f'This action cannot be undone.'
        remove = message_dialogs.warning_question_dialog(self, f'Delete {count_text}?', text)
        if remove:
            list_model = self.user_list_model if reddit_objects[0].object_type == 'USER' else self.subreddit_list_model
            list_name = list_model.close_session()
            for reddit_object in reddit_objects:
                try:
                    ModelManger.delete_reddit_object(reddit_object, delete_files=delete_files)
                except:
                    self.logger.error('Failed to delete reddit object', extra={'reddit_object': reddit_object.name},
                                      exc_info=True)
            list_model.open_session(list_name=list_name)

    def add_subreddit(self):
        if self.subreddit_list_model.list is None:
            self.add_subreddit_list(list_name='Default')
        add_sub_dialog = AddRedditObjectDialog(self.subreddit_list_model, self)
        add_sub_dialog.exec_()

    def remove_subreddit(self):
        """
        Gets the currently selected index from the subreddit list and the current subreddit list model and calls a
        method to remove the object at the current index
        """
        self.remove_reddit_object(self.get_selected_subreddits(), self.subreddit_list_model)

    def check_existing_object_for_download(self, existing_tuple: tuple):
        """
        Called when existing names are added to a list.  Takes a tuple containing the list type, list of existing id's,
        and a list of existing names.  If the global settings indicate to download reddit objects on add, a prompt asks
        the user if they wish to download the existing users, and their response is handled appropriately.
        :param existing_tuple: A tuple: (reddit_object_type, reddit_object_id_list, reddit_object_name_list).
        """
        if self.settings_manager.download_on_add:
            ro_type, id_list, name_list = existing_tuple
            dialog = ExistingRedditObjectAddDialog(ro_type, *name_list)
            rep = dialog.exec_()
            if rep:
                self.add_to_download(*id_list)

    def check_new_object_for_download(self, reddit_object_id):
        if self.settings_manager.download_on_add:
            self.add_to_download(reddit_object_id)

    def scroll_to_new(self, index, list_type):
        """
        If specified in the settings manager to do so, the list view of the supplied list type will scroll to the
        reddit object which was most recently added.
        :param index: The index in the reddit object list of the most recent object.
        :param list_type: The type of list to which a reddit object was added.  Used to decide which view should scroll.
        """
        if self.settings_manager.scroll_to_last_added:
            if list_type == 'USER':
                view = self.user_list_view
                index = self.user_list_model.createIndex(index, 0)
            else:
                view = self.subreddit_list_view
                index = self.subreddit_list_model.createIndex(index, 0)
            view.scrollTo(index)

    def display_database_dialog(self, **kwargs):
        """
        Creates the database dialog instance with the supplied kwargs, connects the appropriate signals, and returns the
        dialog to be used by the caller.
        """
        database_dialog = DatabaseDialog(**kwargs)
        database_dialog.update_post_score_signal.connect(self.update_post_scores)
        database_dialog.update_post_comments_signal.connect(self.fetch_new_post_comments)
        database_dialog.show()

    def open_database_view_dialog(self):
        kwargs = {
            'filters': self.settings_manager.database_view_default_filters['Database View']
        }
        self.display_database_dialog(save_settings=True, **kwargs)

    def open_download_sessions_dialog(self):
        kwargs = {
            'focus_model': 'DOWNLOAD_SESSION',
            'download_session_sort': 'start_time',
            'download_session_desc': True,
            'filters': self.settings_manager.database_view_default_filters['Download Session View']
        }
        self.display_database_dialog(**kwargs)

    def open_reddit_objects_dialog(self):
        kwargs = {
            'focus_model': 'REDDIT_OBJECT',
            'reddit_object_sort': 'name',
            'visible_models': ['REDDIT_OBJECT'],
            'filters': self.settings_manager.database_view_default_filters['Reddit Object View']
        }
        self.display_database_dialog(**kwargs)

    def open_posts_dialog(self):
        kwargs = {
            'focus_model': 'POST',
            'reddit_object_sort': 'title',
            'visible_models': ['POST'],
            'filters': self.settings_manager.database_view_default_filters['Post View']
        }
        self.display_database_dialog(**kwargs)

    def open_content_dialog(self):
        kwargs = {
            'focus_model': 'CONTENT',
            'reddit_object_sort': 'title',
            'visible_models': ['CONTENT'],
            'filters': self.settings_manager.database_view_default_filters['Content View']
        }
        self.display_database_dialog(**kwargs)

    def open_comment_dialog(self):
        kwargs = {
            'focus_model': 'COMMENT',
            'reddit_object_sort': 'post_title',
            'visible_models': ['COMMENT'],
            'filters': self.settings_manager.database_view_default_filters['Comment View']
        }
        self.display_database_dialog(**kwargs)

    def open_failed_extraction_dialog(self):
        kwargs = {
            'focus_model': 'POST',
            'download_session_sort': 'start_time',
            'download_session_desc': True,
            'post_sort': 'title',
            'visible_models': ['DOWNLOAD_SESSION', 'POST'],
            'filters': [
                {'model': 'POST', 'field': 'extracted', 'operator': 'eq', 'value': False},
            ]
        }
        kwargs['filters'].extend(self.settings_manager.database_view_default_filters['Failed Extract View'])
        self.display_database_dialog(**kwargs)

    def open_failed_downloads_dialog(self):
        kwargs = {
            'focus_model': 'CONTENT',
            'download_session_sort': 'start_time',
            'download_session_desc': True,
            'content_sort': 'title',
            'visible_models': ['DOWNLOAD_SESSION', 'CONTENT'],
            'filters': [
                {'model': 'CONTENT', 'field': 'downloaded', 'operator': 'eq', 'value': False}
            ]
        }
        kwargs['filters'].extend(self.settings_manager.database_view_default_filters['Failed Downloads View'])
        self.display_database_dialog(**kwargs)

    def open_selected_reddit_object_dialog(self, selected_id, secondary_view):
        kwargs = {
            'focus_model': 'REDDIT_OBJECT',
            'selected_model_id': selected_id,
            'reddit_object_sort': 'name',
            'visible_models': ['REDDIT_OBJECT', secondary_view],
            'filters': self.settings_manager.database_view_default_filters['Reddit Object View']
        }
        self.display_database_dialog(**kwargs)

    def open_database_statistics_dialog(self):
        dialog = DatabaseStatisticsDialog()
        dialog.exec_()

    def started_download_gui_shift(self):
        """Changes parts of the gui to display differently while there is a download session currently in progress."""
        self.running = True
        if self.settings_manager.clear_messages_on_run:
            self.output_view_model.clear()
        self.init_progress_bar()
        self.downloaded = 0
        self.potential_downloads = 0
        self.statusbar.clearMessage()
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(True)
        self.shift_download_buttons()
        self.setup_run_timer()
        Message.send_status_tray('Starting download')
        self.system_tray_icon.setToolTip('Downloader For Reddit (running)')

    def finished_download_gui_shift(self):
        """Resets the GUI shift that happens when a download session is started."""
        self.running = False
        self.progress_bar.setVisible(False)
        self.potential_downloads = 0
        self.shift_download_buttons()
        self.timer_widget.setVisible(False)
        self.run_time = 0
        # list models are sorted to refresh the display list and
        self.user_list_model.refresh_session()
        self.subreddit_list_model.refresh_session()
        self.check_invalid()
        self.system_tray_icon.setToolTip('Downloader For Reddit')

    def shift_download_buttons(self):
        self.download_button.setVisible(not self.running)
        self.soft_stop_download_button.setVisible(self.running)
        self.terminate_download_button.setVisible(self.running)

    def check_invalid(self):
        if len(self.invalid_list) > 0:
            dialog = InvalidRedditObjectDialog(self.invalid_list)
            dialog.exec_()
            for ro in dialog.invalid_ros:
                if ro.remove:
                    if ro.status == 'deleted':
                        rename = self.settings_manager.rename_invalidated_download_folders
                    else:
                        rename = False
                    self.remove_problem_reddit_object(ro.id, rename, ro.status)

    def finish_progress_bar(self):
        """
        Changes the progress bar text to show that it is complete and also moves the progress bar value to the maximum
        if for whatever reason it was not already there
        """
        self.progress_label.setText('Download complete - Downloaded: %s' % self.potential_downloads)
        if self.progress_bar.value() < self.progress_bar.maximum():
            self.progress_bar.setValue(self.progress_bar.maximum())

    def setup_run_timer(self):
        """
        Starts the run timer and sets the appropriate displays visible to the user.
        """
        self.run_timer.start(1000)
        self.timer_widget.setVisible(True)
        self.perpetual_run_label.setVisible(self.settings_manager.perpetual_download)

    def update_run_time(self):
        self.run_time += 1
        self.timer_label.setText(system_util.format_duration_short(self.run_time))

    def open_settings_dialog(self, **kwargs):
        """Displays the main settings dialog and calls methods that update each reddit object if needed."""
        settings = SettingsDialog(parent=self, **kwargs)
        settings.exec_()

    def sign_out(self):
        reddit_utils.delete_token()
        Message.send_info(f'Signed out of Downloader for Reddit.')
        self.connect_reddit_account_menu_item.setText(f"Connect Reddit Account")
        self.connect_reddit_account_menu_item.triggered.disconnect(self.sign_out)
        self.connect_reddit_account_menu_item.triggered.connect(self.start_oauth_flow)

    def start_oauth_flow(self):
        authorization_url = QUrl("https://www.reddit.com/api/v1/authorize")
        access_url = QUrl("https://www.reddit.com/api/v1/access_token")

        manager = QNetworkAccessManager(self)
        reply_handler = QOAuthHttpServerReplyHandler(8086)
        oauth = QOAuth2AuthorizationCodeFlow(reddit_utils.CLIENT_ID, authorization_url, access_url, manager, self)
        oauth.granted.connect(self.finish_oauth_flow)
        oauth.authorizeWithBrowser.connect(QDesktopServices.openUrl)
        oauth.setReplyHandler(reply_handler)
        oauth.setScope(" ".join(reddit_utils.TOKEN_SCOPES))
        oauth.setUserAgent(reddit_utils.USER_AGENT)

        params = {
            "duration": "permanent"
        }
        oauth.resourceOwnerAuthorization(authorization_url, params)
        self.oauth = oauth

    def finish_oauth_flow(self):
        token = self.oauth.refreshToken()
        reddit_utils.save_token(token)
        user = reddit_utils.check_authorized_connection()
        Message.send_info(f'Downloader for Reddit is now linked to {user}\'s reddit account.')
        self.connect_reddit_account_menu_item.setText(f"Sign out: {user}")
        self.connect_reddit_account_menu_item.disconnect()
        self.connect_reddit_account_menu_item.triggered.connect(self.sign_out)

        self.oauth.replyHandler().close()

    def update_output(self):
        self.output_view_model.update_output_level()

    def display_imgur_client_information(self):
        """Opens a dialog that tells the user how many imgur credits they have remaining"""
        imgur_utils.check_credits()
        reset_date_time = datetime.fromtimestamp(imgur_utils.credit_reset_time)
        reset_time = general_utils.format_datetime(reset_date_time)
        dialog_text = "Remaining Credits: {}\n" \
                      "Reset Time: {}\n".format(imgur_utils.num_credits, reset_time)
        if injector.get_settings_manager().imgur_mashape_key:
            dialog_text += "\nFallback to the commercial API enabled!"
        QMessageBox.information(self, 'Imgur Credits', dialog_text, QMessageBox.Ok)

    def display_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def open_user_manual(self):
        """Opens the user manual using the default PDF viewer"""
        # manual = 'The Downloader For Reddit - User Manual.pdf'
        # if os.path.isfile(os.path.join(os.getcwd(), manual)):
        #     file = os.path.join(os.getcwd(), manual)
        # else:
        #     separator = '/' if not sys.platform == 'win32' else '\\'
        #     containing_folder, current = os.getcwd().rsplit(separator, 1)
        #     file = os.path.join(containing_folder, manual)
        # try:
        #     system_util.open_in_system(file)
        # except FileNotFoundError:
        #     self.logger.error('Unable to open user manual: Manual file not found', exc_info=True)
        #     message_dialogs.user_manual_not_found(self)
        self.logger.warning('Attempt was made to open user manual.  User manual has been removed for beta version.')

    def set_list_order(self, order_by=None, desc=None):
        """Applies the sort and order function to each list model"""
        if order_by is not None:
            self.settings_manager.list_order_method = order_by
        if desc is not None:
            self.settings_manager.order_list_desc = desc
        self.user_list_model.sort_list()
        self.subreddit_list_model.sort_list()

    def closeEvent(self, event):
        """
        As absolutely ridiculous as this is, for some reason if this close event is not set, PyQt outputs a QThread
        error on application close stating that a thread has been destroyed while still running.  I'm not sure if
        having to call this event gives what ever thread it is a couple more nanoseconds to close or if the universe
        thought I had too much hair and decided I should pull it out whilst tracking this problem down.  Either way,
        this useless method stays.
        """
        self.close()

    def close(self):
        self.receiver.stop_run()
        self.scheduler.stop_run()
        self.run_timer.stop()
        self.save_main_window_settings()
        self.settings_manager.save_all()
        super().close()

    def save_main_window_settings(self):
        self.settings_manager.main_window_geom['width'] = self.width()
        self.settings_manager.main_window_geom['height'] = self.height()
        self.settings_manager.main_window_geom['x'] = self.x()
        self.settings_manager.main_window_geom['y'] = self.y()
        self.settings_manager.horizontal_splitter_state = self.horz_splitter.sizes()
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
            system_util.open_in_system(system_util.get_data_directory())
        except Exception:
            self.logger.error('Failed to open data directory', exc_info=True)

    def check_for_updates(self, from_menu):
        """
        Opens and runs the update checker on a separate thread. Sets self.from_menu so that other dialogs know the
        updater has been ran by the user, this will result in different dialog behaviour
        """
        self.start_main_spinner()
        self.update_check_thread = QThread()
        self.update_checker = UpdateChecker()
        self.update_checker.moveToThread(self.update_check_thread)
        self.update_check_thread.started.connect(self.update_checker.run)
        if from_menu:
            self.update_checker.update_available_signal.connect(self.update_dialog)
            self.update_checker.no_update_signal.connect(self.no_update_available_dialog)
        else:
            self.update_checker.update_available_signal.connect(self.display_update)
        self.update_checker.finished.connect(self.stop_spinner)
        self.update_checker.finished.connect(self.update_check_thread.quit)
        self.update_checker.finished.connect(self.update_checker.deleteLater)
        self.update_check_thread.finished.connect(self.update_check_thread.deleteLater)
        self.update_check_thread.start()

    def display_update(self, latest_version):
        if self.settings_manager.ignore_update != latest_version:
            self.update_dialog(latest_version)

    def update_dialog(self, update_variables):
        """Opens the update dialog"""
        update_checker = UpdateDialog(update_variables, self)
        update_checker.show()
        update_checker.exec_()

    def no_update_available_dialog(self):
        message_dialogs.up_to_date_message(self)

    def display_ffmpeg_info_dialog(self):
        dialog = FfmpegInfoDialog(self)
        dialog.exec_()

    def check_ffmpeg(self):
        """
        Checks that ffmpeg is installed on the host system and notifies the user if it is not installed.  Will also
        disable reddit video download depending on the user input through the dialog.
        """
        if not video_merger.ffmpeg_valid and self.settings_manager.display_ffmpeg_warning:
            disable = message_dialogs.ffmpeg_warning(self)
            self.settings_manager.download_reddit_hosted_videos = not disable
            self.settings_manager.display_ffmpeg_warning = False

    def output_command_line_options(self):
        """
        Outputs the command line options for users that run a compiled version of the application.  When compiled, the
        cli output will not be seen by the user.  This shows them what options are available.
        """
        faux_file = io.StringIO()
        cli = CLI()
        cli.parser.print_help(faux_file)
        Message.send_requested(faux_file.getvalue())

    def setup_system_tray_icon(self):
        menu = QMenu()
        menu.addAction('Download User list', self.download_user_list)
        menu.addAction('Download Subreddit List', self.download_subreddit_list)
        menu.addAction('Download User List Constrained', self.download_user_list_constrained)
        menu.addSeparator()
        menu.addAction('Hide Window', self.hide)
        menu.addAction('Show Window', self.activate_window)
        menu.addSeparator()
        menu.addAction('Remove Icon', lambda: self.system_tray_icon.hide())
        menu.addAction('Exit', self.close)

        self.system_tray_icon.setContextMenu(menu)
        self.system_tray_icon.activated.connect(self.handle_tray_icon_click)
        self.system_tray_icon.messageClicked.connect(self.activate_window)
        self.system_tray_icon.setToolTip('Downloader For Reddit')
        if self.settings_manager.show_system_tray_icon:
            self.system_tray_icon.show()

    def handle_tray_icon_click(self, click_type):
        if click_type == QSystemTrayIcon.DoubleClick:
            self.activate_window()

    def activate_window(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def set_tray_icon_message(self, message):
        if not QApplication.focusWindow() and self.settings_manager.show_system_tray_notifications:
            self.system_tray_icon.showMessage('Downloader For Reddit', message.message, self.tray_icon_image,
                                              self.settings_manager.tray_icon_message_display_length * 1000)

    def minimize_to_tray(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.system_tray_icon.show()
            self.hide()
        else:
            Message.send_error('System tray icon is not available for this system.')
