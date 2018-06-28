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
from PyQt5.QtCore import QSettings
import logging

from Persistence.ObjectStateHandler import ObjectStateHandler
from Persistence.ObjectUpdater import ObjectUpdater
from version import __version__


class SettingsManager:

    def __init__(self):
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.settings = QSettings('SomeGuySoftware', 'RedditDownloader')
        self.load_settings()
        if self.check_first_run():
            ObjectUpdater.check_settings_manager(self)

        self.nsfw_filter_dict = {
            'Include': 'INCLUDE',
            'Do Not Include': 'EXCLUDE',
            'Include Only NSFW': 'ONLY'
        }

    def check_first_run(self):
        cached_version = self.settings.value("cached_version", "v0.0.0", type=str)
        if cached_version != __version__:
            self.logger.info('First run of new version',
                             extra={'new_version': __version__, 'old_version': cached_version})
            return True
        else:
            return False

    def load_settings(self):
        # region Core Settings
        self.do_not_notify_update = self.settings.value("do_not_notify_update", "v0.0.0", type=str)
        self.last_update = self.settings.value('last_update', None, type=str)
        self.total_files_downloaded = self.settings.value('total_files_downloaded', 0, type=int)
        self.auto_save = self.settings.value('auto_save', False, type=bool)
        self.imgur_client_id = self.settings.value('imgur_client_id', None, type=str)
        self.imgur_client_secret = self.settings.value('imgur_client_secret', None, type=str)
        self.auto_display_failed_list = self.settings.value("auto_display_failed_list", True, type=bool)

        self.restrict_by_score = self.settings.value('restrict_by_score', False, type=bool)
        self.score_limit_operator = self.settings.value('score_limit_operator', 'GREATER', type=str)
        self.post_score_limit = self.settings.value("post_score_limit", 3000, type=int)

        self.subreddit_sort_method = self.settings.value('subreddit_sort_method', 'HOT', type=str)
        self.subreddit_sort_top_method = self.settings.value('subreddit_sort_top_method', 'DAY', type=str)

        self.post_limit = self.settings.value('post_limit', 25, type=int)

        self.restrict_by_date = self.settings.value('restrict_by_date', False, type=bool)
        self.restrict_by_custom_date = self.settings.value("restrict_by_custom_date", False, type=bool)
        self.custom_date = self.settings.value('settings_custom_date', 86400, type=int)
        if self.custom_date < 86400:
            self.custom_date = 86400

        self.download_videos = self.settings.value('download_video', True, type=bool)
        self.download_images = self.settings.value('download_images', True, type=bool)
        self.avoid_duplicates = self.settings.value('avoid_duplicates', True, type=bool)

        self.nsfw_filter = self.settings.value('nsfw_filter', 'INCLUDE', type=str)

        self.save_subreddits_by = self.settings.value('save_subreddits_by', 'Subreddit Name', type=str)
        self.name_downloads_by = self.settings.value('name_downloads_by', 'Image/Album Id', type=str)

        default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.save_directory = self.settings.value("save_directory", default_folder, type=str)
        self.max_download_thread_count = self.settings.value('max_download_thread_count', 4, type=int)
        self.save_undownloaded_content = self.settings.value("save_undownloaded_content", True, type=bool)
        self.save_failed_extracts = self.settings.value('save_failed_extracts', True, type=bool)
        self.set_file_modified_date = self.settings.value('set_file_modified_date', False, type=bool)
        # endregion

        # region Display Settings
        self.tooltip_display_dict = {
            'name': self.settings.value('tooltip_name', True, type=bool),
            'do_not_edit': self.settings.value('tooltip_do_not_edit', False, type=bool),
            'last_download_date': self.settings.value('tooltip_last_download_date', True, type=bool),
            'custom_date_limit': self.settings.value('tooltip_custom_date_limit', False, type=bool),
            'post_limit': self.settings.value('tooltip_post_limit', False, type=bool),
            'name_downloads_by': self.settings.value('tooltip_name_downloads_by', False, type=bool),
            'subreddit_save_method': self.settings.value('tooltip_subreddit_save_method', False, type=bool),
            'save_path': self.settings.value('tooltip_save_path', False, type=bool),
            'download_videos': self.settings.value('tooltip_download_videos', False, type=bool),
            'download_images': self.settings.value('tooltip_download_images', False, type=bool),
            'avoid_duplicates': self.settings.value('tooltip_avoid_duplicates', False, type=bool),
            'nsfw_filter': self.settings.value('tooltip_nsfw_filter', False, type=bool),
            'saved_content_count': self.settings.value('tooltip_saved_content_count', False, type=bool),
            'saved_submission_count': self.settings.value('tooltip_saved_submission_count', False, type=bool),
            'total_download_count': self.settings.value('tooltip_total_download_count', True, type=bool),
            'added_on_date': self.settings.value('tooltip_added_on_date', False, type=bool)
        }
        self.gif_display_method = self.settings.value('gif_display_method', 'PLACEHOLDER', str)
        # endregion

        # region Main Window GUI
        self.main_window_geom = self.settings.value('main_window_geometry', None)
        self.horz_splitter_state = self.settings.value('horz_splitter_state', None)
        self.vert_splitter_state = self.settings.value('vert_splitter_state', None)
        self.list_sort_method = self.settings.value('list__sort_method', 0, type=int)
        self.list_order_method = self.settings.value('list_order_method', 0, type=int)
        self.download_users = self.settings.value("download_users", False, type=bool)
        self.download_subreddits = self.settings.value("download_subreddits", False, type=bool)
        # endregion

        self.reddit_object_settings_dialog_geom = self.settings.value('reddit_object_settings_dialog_geom', None)
        self.reddit_object_content_icons_full_width = self.settings.value('reddit_object_content_icons_full_width',
                                                                          False, type=bool)
        self.reddit_object_content_icon_size = self.settings.value('reddit_object_content_icon_size', 110, type=int)
        self.current_reddit_object_settings_item_display_list = \
            self.settings.value('current_reddit_object_settings_item_display_list', 'previous_downloads', type=str)
        self.reddit_object_settings_dialog_splitter_state = self.settings.value(
            'reddit_object_settings_dialog_splitter_state', None)
        # endregion

        # region UserFinder GUI
        self.user_finder_GUI_geom = self.settings.value('user_finder_GUI_geometry', None)
        self.user_finder_splitter_one_state = self.settings.value('user_finder_splitter_one_state', None)
        self.user_finder_splitter_two_state = self.settings.value('user_finder_splitter_two_state', None)
        self.user_finder_splitter_three_state = self.settings.value('user_finder_splitter_three_state', None)
        self.user_finder_top_sort_method = self.settings.value('user_finder_top_sort_method', 'MONTH', type=str)
        self.user_finder_show_users_reddit_page = self.settings.value('user_finder_show_users_reddit_page', False,
                                                                      type=bool)
        self.user_finder_filter_by_score = self.settings.value('user_finder_filter_by_score', False, type=bool)
        self.user_finder_score_limit = self.settings.value('user_finder_score_limit', 3000, type=int)
        self.user_finder_post_limit = self.settings.value('user_finder_post_limit', 5, type=int)

        self.user_finder_subreddit_list = self.settings.value('user_finder_subreddit_list', ['filler'], type=str)
        self.user_finder_user_blacklist = self.settings.value('user_finder_blacklist', ['filler'], type=str)

        self.user_finder_user_list_sort_method = self.settings.value('user_finder_user_list_sort_method', 'NAME',
                                                                     type=str)
        self.user_finder_user_list_sort_order = self.settings.value('user_finder_user_list_sort_order', 'ASC', type=str)
        self.user_finder_preview_size = self.settings.value('user_finder_preview_size', 110, type=int)
        # endregion

        # region UserFinderSettings
        self.user_finder_sample_size = self.settings.value('user_finder_sample_size', 5, type=int)
        self.user_finder_sample_type_method = self.settings.value('user_finder_sample_type_method', 'TOP',
                                                                  type=str)
        self.user_finder_run_with_main = self.settings.value('user_finder_run_with_main', False, type=bool)
        self.user_finder_auto_add_found = self.settings.value('user_finder_auto_add_found', False, type=bool)
        self.user_finder_auto_add_user_list = self.settings.value('user_finder_auto_add_user_list', None, type=str)

        self.user_finder_auto_run_silent = self.settings.value('user_finder_auto_run_silent', False, type=bool)
        self.user_finder_double_click_operation = self.settings.value('user_finder_double_click_operation', 'DIALOG',
                                                                      type=str)
        # endregion

        # region UserFinderSettingsGUISettings
        self.user_finder_settings_gui_geom = self.settings.value('user_finder_settings_gui_geom', None)
        # endregion

        # region Misc Dialogs
        self.settings_dialog_geom = self.settings.value('settings_dialog_geom')
        self.add_user_dialog_geom = self.settings.value("add_user_dialog_geom")
        self.failed_downloads_dialog_geom = self.settings.value("failed_downloads_dialog_geom")
        self.failed_downloads_dialog_splitter_state = self.settings.value("failed_downloads_dialog_splitter_state", None)
        self.about_dialog_geom = self.settings.value("about_dialog_geom")
        self.update_dialog_geom = self.settings.value("update_dialog_geom")
        # endregion

    def load_picked_objects(self):
        return ObjectStateHandler.load_pickled_state()

    def save_pickle_objects(self, object_dict):
        object_handler = ObjectStateHandler()
        return object_handler.save_pickled_state(object_dict)

    def save_all(self):
        self.save_core_settings()
        self.save_main_window()
        self.save_reddit_object_settings_dialog()

    def save_core_settings(self):
        self.settings.setValue('cached_version', __version__)
        self.settings.setValue("last_update", self.last_update)
        self.settings.setValue("total_files_downloaded", self.total_files_downloaded)
        self.settings.setValue("auto_save", self.auto_save)
        self.settings.setValue("imgur_client_id", self.imgur_client_id)
        self.settings.setValue("imgur_client_secret", self.imgur_client_secret)
        self.settings.setValue("auto_display_failed_list", self.auto_display_failed_list)
        self.settings.setValue("restrict_by_score", self.restrict_by_score)
        self.settings.setValue("score_limit_operator", self.score_limit_operator)
        self.settings.setValue("post_score_limit", self.post_score_limit)
        self.settings.setValue("subreddit_sort_method", self.subreddit_sort_method)
        self.settings.setValue("subreddit_sort_top_method", self.subreddit_sort_top_method)
        self.settings.setValue("post_limit", self.post_limit)
        self.settings.setValue("restrict_by_date", self.restrict_by_date)
        self.settings.setValue("restrict_by_custom_date", self.restrict_by_custom_date)
        self.settings.setValue("settings_custom_date", self.custom_date)
        self.settings.setValue("download_video", self.download_videos)
        self.settings.setValue("download_images", self.download_images)
        self.settings.setValue("avoid_duplicates", self.avoid_duplicates)
        self.settings.setValue('nsfw_filter', self.nsfw_filter)
        self.settings.setValue("save_subreddits_by", self.save_subreddits_by)
        self.settings.setValue("name_downloads_by", self.name_downloads_by)
        self.settings.setValue("save_directory", self.save_directory)
        self.settings.setValue("max_download_thread_count", self.max_download_thread_count)
        self.settings.setValue("save_undownloaded_content", self.save_undownloaded_content)
        self.settings.setValue('save_failed_extracts', self.save_failed_extracts)
        self.settings.setValue('set_file_modified_date', self.set_file_modified_date)

    def save_display_settings(self):
        self.settings.setValue('tooltip_name', self.tooltip_display_dict['name'])
        self.settings.setValue('tooltip_do_not_edit', self.tooltip_display_dict['do_not_edit'])
        self.settings.setValue('tooltip_last_download_date', self.tooltip_display_dict['last_download_date'])
        self.settings.setValue('tooltip_custom_date_limit', self.tooltip_display_dict['custom_date_limit'])
        self.settings.setValue('tooltip_post_limit', self.tooltip_display_dict['post_limit'])
        self.settings.setValue('tooltip_name_downloads_by', self.tooltip_display_dict['name_downloads_by'])
        self.settings.setValue('tooltip_subreddit_save_method', self.tooltip_display_dict['subreddit_save_method'])
        self.settings.setValue('tooltip_save_path', self.tooltip_display_dict['save_path'])
        self.settings.setValue('tooltip_download_videos', self.tooltip_display_dict['download_videos'])
        self.settings.setValue('tooltip_download_images', self.tooltip_display_dict['download_images'])
        self.settings.setValue('tooltip_avoid_duplicates', self.tooltip_display_dict['avoid_duplicates'])
        self.settings.setValue('tooltip_nsfw_filter', self.tooltip_display_dict['nsfw_filter'])
        self.settings.setValue('tooltip_saved_content_count', self.tooltip_display_dict['saved_content_count'])
        self.settings.setValue('tooltip_saved_submission_count', self.tooltip_display_dict['saved_submission_count'])
        self.settings.setValue('tooltip_total_download_count', self.tooltip_display_dict['total_download_count'])
        self.settings.setValue('tooltip_added_on_date', self.tooltip_display_dict['added_on_date'])
        self.settings.setValue('gif_display_method', self.gif_display_method)

    def save_main_window(self):
        self.settings.setValue("main_window_geometry", self.main_window_geom)
        self.settings.setValue('horz_splitter_state', self.horz_splitter_state)
        self.settings.setValue('vert_splitter_state', self.vert_splitter_state)
        self.settings.setValue("list__sort_method", self.list_sort_method)
        self.settings.setValue("list_order_method", self.list_order_method)
        self.settings.setValue("download_users", self.download_users)
        self.settings.setValue("download_subreddits", self.download_subreddits)

    def save_reddit_object_settings_dialog(self):
        self.settings.setValue('reddit_object_settings_dialog_geom', self.reddit_object_settings_dialog_geom)
        self.settings.setValue('reddit_object_settings_dialog_splitter_state',
                               self.reddit_object_settings_dialog_splitter_state)
        self.settings.setValue('reddit_object_content_icons_full_width', self.reddit_object_content_icons_full_width)
        self.settings.setValue('reddit_object_content_icon_size', self.reddit_object_content_icon_size)
        self.settings.setValue('current_reddit_object_settings_item_display_list',
                               self.current_reddit_object_settings_item_display_list)

    def save_user_finder(self):
        self.settings.setValue('user_finder_show_users_reddit_page', self.user_finder_show_users_reddit_page)
        self.settings.setValue('user_finder_sample_size', self.user_finder_sample_size)
        self.settings.setValue('user_finder_sample_type_method', self.user_finder_sample_type_method)
        self.settings.setValue('user_finder_run_with_main', self.user_finder_run_with_main)
        self.settings.setValue('user_finder_auto_add_found', self.user_finder_auto_add_found)
        self.settings.setValue('user_finder_auto_add_user_list', self.user_finder_auto_add_user_list)
        self.settings.setValue('user_finder_auto_run_silent', self.user_finder_auto_run_silent)
        self.settings.setValue('user_finder_preview_size', self.user_finder_preview_size)
        self.settings.setValue('user_finder_double_click_operation', self.user_finder_double_click_operation)

    def save_user_finder_dialog(self):
        self.settings.setValue('user_finder_GUI_geometry', self.user_finder_GUI_geom)
        self.settings.setValue('user_finder_splitter_one_state', self.user_finder_splitter_one_state)
        self.settings.setValue('user_finder_splitter_two_state', self.user_finder_splitter_two_state)
        self.settings.setValue('user_finder_splitter_three_state', self.user_finder_splitter_three_state)
        self.settings.setValue('user_finder_top_sort_method', self.user_finder_top_sort_method)
        self.settings.setValue('user_finder_filter_by_score', self.user_finder_filter_by_score)
        self.settings.setValue('user_finder_score_limit', self.user_finder_score_limit)
        self.settings.setValue('user_finder_post_limit', self.user_finder_post_limit)
        self.settings.setValue('user_finder_subreddit_list', self.user_finder_subreddit_list)
        self.settings.setValue('user_finder_blacklist', self.user_finder_user_blacklist)
        self.settings.setValue('user_finder_preview_size', self.user_finder_preview_size)
        self.settings.setValue('user_finder_user_list_sort_method', self.user_finder_user_list_sort_method)
        self.settings.setValue('user_finder_user_list_sort_order', self.user_finder_user_list_sort_order)

    def save_user_finder_settings_dialog(self):
        self.settings.setValue('user_finder_settings_gui_geom', self.user_finder_settings_gui_geom)

    def save_settings_dialog(self):
        self.settings.setValue('settings_dialog_geom', self.settings_dialog_geom)

    def save_add_user_dialog(self):
        self.settings.setValue("add_user_dialog_geom", self.add_user_dialog_geom)

    def save_failed_downloads_dialog(self):
        self.settings.setValue("failed_downloads_dialog_geom", self.failed_downloads_dialog_geom)
        self.settings.setValue("failed_downloads_dialog_splitter_state", self.failed_downloads_dialog_splitter_state)

    def save_about_dialog(self):
        self.settings.setValue("about_dialog_geom", self.about_dialog_geom)

    def save_update_dialog(self):
        self.settings.setValue("do_not_notify_update", self.do_not_notify_update)
        self.settings.setValue("update_dialog_geom", self.update_dialog_geom)

    @property
    def json(self):
        """
        Makes and returns a json dict of all of the download relevant settings to be logged.
        :return: A dict of download relevant settings.
        :rtype: dict
        """
        return {
            'imgur_client_valid': self.check_imgur_client(),
            'restrict_by_score': self.restrict_by_score,
            'score_limit_operator': self.score_limit_operator,
            'score_limit': self.post_score_limit,
            'subreddit_sort_method': self.subreddit_sort_method,
            'subreddit_sort_top_method': self.subreddit_sort_top_method,
            'post_limit': self.post_limit,
            'restrict_by_date': self.restrict_by_date,
            'restrict_by_custom_date': self.restrict_by_custom_date,
            'custom_date': self.custom_date,
            'download_videos': self.download_videos,
            'download_images': self.download_images,
            'avoid_duplicates': self.avoid_duplicates,
            'nsfw_filter': self.nsfw_filter,
            'save_subreddits_by': self.save_subreddits_by,
            'name_downloads_by': self.name_downloads_by,
            'save_directory': self.save_directory,
            'max_download_thread_count': self.max_download_thread_count,
            'save_undownloaded_content': self.save_undownloaded_content
        }

    def check_imgur_client(self):
        return self.imgur_client_id is not None and self.imgur_client_secret is not None
