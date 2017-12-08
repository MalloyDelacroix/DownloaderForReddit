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
import shelve

from Persistence.ObjectLoader import ObjectLoader
from version import __version__


class SettingsManager:

    def __init__(self):
        self.settings = QSettings('SomeGuySoftware', 'RedditDownloader')
        self.load_settings()
        self.count = 0

    def check_first_run(self):
        cached_version = self.settings.value("cached_version", "v0.0.0", type=str)
        return cached_version != __version__

    def load_settings(self):
        # region Core Settings
        self.do_not_notify_update = self.settings.value("do_not_notify_update", "v0.0.0", type=str)
        self.first_run = self.settings.value('first_run', True, type=bool)
        self.last_update = self.settings.value('last_update', None, type=str)
        self.total_files_downloaded = self.settings.value('total_files_downloaded', 0, type=int)
        self.auto_save = self.settings.value('auto_save', False, type=bool)
        self.imgur_client_id = self.settings.value('imgur_client_id', None, type=str)
        self.imgur_client_secret = self.settings.value('imgur_client_secret', None, type=str)
        self.auto_display_failed_list = self.settings.value("auto_display_failed_list", True, type=bool)

        self.restrict_by_score = self.settings.value('restrict_by_score', False, type=bool)
        self.score_limit_operator = self.settings.value("score_limit_operator", 0, type=int)
        self.post_score_limit = self.settings.value("post_score_limit", 3000, type=int)

        self.subreddit_sort_method = self.settings.value('subreddit_sort_method', 0, type=int)
        self.subreddit_sort_top_method = self.settings.value('subreddit_sort_top_method', 0, type=int)

        self.post_limit = self.settings.value('post_limit', 25, type=int)

        self.restrict_by_date = self.settings.value('restrict_by_date', False, type=bool)
        self.restrict_by_custom_date = self.settings.value("restrict_by_custom_date", False, type=bool)
        self.custom_date = self.settings.value('settings_custom_date', 86400, type=int)
        if self.custom_date < 86400:
            self.custom_date = 86400

        self.download_videos = self.settings.value('download_video', True, type=bool)
        self.download_images = self.settings.value('download_images', True, type=bool)
        self.avoid_duplicates = self.settings.value('avoid_duplicates', True, type=bool)

        self.save_subreddits_by = self.settings.value('save_subreddits_by', 'Subreddit Name', type=str)
        self.name_downloads_by = self.settings.value('name_downloads_by', 'Image/Album Id', type=str)

        default_folder = os.path.expanduser("~") + "/Downloads/"
        self.save_directory = self.settings.value("save_directory", default_folder, type=str)
        self.max_download_thread_count = self.settings.value('max_download_thread_count', 4, type=int)
        self.save_undownloaded_content = self.settings.value("save_undownloaded_content", True, type=bool)
        # endregion

        # region Main Window GUI
        self.main_window_geom = self.settings.value('main_window_geometry', None)
        self.list_sort_method = self.settings.value('list__sort_method', 0, type=int)
        self.list_order_method = self.settings.value('list_order_method', 0, type=int)
        self.download_users = self.settings.value("download_users", False, type=bool)
        self.download_subreddits = self.settings.value("download_subreddits", False, type=bool)
        # endregion

        # region UserSettingsDialog
        self.user_settings_dialog_geom = self.settings.value('user_settings_dialog_geometry')
        self.user_content_icons_full_width = self.settings.value('user_content_icons_full_width', False, type=bool)
        self.user_content_icon_size = self.settings.value('user_content_icon_size', 110, type=int)
        self.current_user_settings_item_display_list = self.settings.value('current_item_display_list',
                                                                           'previous_downloads', type=str)
        # endregion

        # region SubredditSettingsDialog
        self.subreddit_content_icons_full_width = self.settings.value('subreddit_content_icons_full_width', False,
                                                                      type=bool)
        self.subreddit_content_icon_size = self.settings.value('subreddit_content_icon_size', 110, type=int)
        # endregion

        # region UserFinder GUI
        self.user_finder_GUI_geom = self.settings.value('user_finder_GUI_geometry')
        self.user_finder_subreddit_watchlist = self.settings.value('sub_watchlist', ['filler'], type=str)
        self.user_finder_user_blacklist = self.settings.value('user_blacklist', ['filler'], type=str)

        self.user_finder_sort_method = self.settings.value("user_finder_sort_method", 0, type=int)
        self.user_finder_watch_list_score_limit = self.settings.value("user_finder_watchlist_score_limit", 5000, type=int)
        self.user_finder_download_sample_size = self.settings.value("user_finder_watchlist_sample_size", 1, type=int)
        self.user_finder_run_with_main = self.settings.value("user_finder_run_with_main", False, type=bool)
        self.user_finder_auto_add_users = self.settings.value("user_finder_auto_add_users", False, type=bool)
        self.user_finder_add_to_index = self.settings.value("user_finder_add_to_index", 0, type=int)

        self.user_finder_content_list_icons_full_width = self.settings.value("user_finder_content_list_icons_full_size",
                                                                             False, type=bool)
        self.user_finder_content_list_icon_size = self.settings.value("user_finder_content_list_icon_size", 110, type=int)
        # endregion

        # region Misc Dialogs
        self.add_user_dialog_geom = self.settings.value("add_user_dialog_geom")
        self.failed_downloads_dialog_geom = self.settings.value("failed_downloads_dialog_geom")
        self.about_dialog_geom = self.settings.value("about_dialog_geom")
        self.update_dialog_geom = self.settings.value("update_dialog_geom")
        # endregion

    def load_picked_objects(self):
        object_loader = ObjectLoader()
        return object_loader.load_pickled_state()

    # def load_pickeled_state(self):
    #     """Attempts to load the user and subreddit list from the pickled state and returns a list of the items loaded"""
    #     user_view_chooser_dict = {}
    #     subreddit_view_chooser_dict = {}
    #     with shelve.open('save_file', 'c') as shelf:
    #         # try:
    #         user_list_models = shelf['user_list_models']
    #         subreddit_list_models = shelf['subreddit_list_models']
    #         last_user_view = shelf['current_user_view']
    #         last_subreddit_view = shelf['current_subreddit_view']
    #
    #         for name, user_list in user_list_models.items():
    #             x = ListModel(name, 'user')
    #             x.reddit_object_list = user_list
    #             x.display_list = [i.name for i in user_list]
    #             user_view_chooser_dict[x.name] = x
    #
    #         for name, subreddit_list in subreddit_list_models.items():
    #             x = ListModel(name, 'subreddit')
    #             x.reddit_object_list = subreddit_list
    #             x.display_list = [i.name for i in subreddit_list]
    #             subreddit_view_chooser_dict[x.name] = x
    #
    #         return [user_view_chooser_dict, subreddit_view_chooser_dict, last_user_view, last_subreddit_view]
    #
    #         # except KeyError:
    #         #     pass
    #
    # def save_pickle_state(self, user_list_models, subreddit_list_models, current_user_view, current_subreddit_view):
    #     try:
    #         with shelve.open("save_file", "c") as shelf:
    #             shelf['user_list_models'] = user_list_models
    #             shelf['subreddit_list_models'] = subreddit_list_models
    #             shelf['current_user_view'] = current_user_view
    #             shelf['current_subreddit_view'] = current_subreddit_view
    #             return True
    #     except:
    #         return False

    def save_all(self):
        self.save_core_settings()
        self.save_main_window()
        self.save_user_settings_dialog()
        self.save_subreddit_settings_dialog()

    def save_core_settings(self):
        self.settings.setValue("first_run", self.first_run)
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
        self.settings.setValue("save_subreddits_by", self.save_subreddits_by)
        self.settings.setValue("name_downloads_by", self.name_downloads_by)
        self.settings.setValue("save_directory", self.save_directory)
        self.settings.setValue("max_download_thread_count", self.max_download_thread_count)
        self.settings.setValue("save_undownloaded_content", self.save_undownloaded_content)

    def save_main_window(self):
        self.settings.setValue("main_window_geometry", self.main_window_geom)
        self.settings.setValue("list__sort_method", self.list_sort_method)
        self.settings.setValue("list_order_method", self.list_order_method)
        self.settings.setValue("download_users", self.download_users)
        self.settings.setValue("download_subreddits", self.download_subreddits)

    def save_user_settings_dialog(self):
        self.settings.setValue('user_settings_dialog_geometry', self.user_settings_dialog_geom)
        self.settings.setValue('user_content_icons_full_width', self.user_content_icons_full_width)
        self.settings.setValue('user_content_icon_size', self.user_content_icon_size)
        self.settings.setValue('current_item_display_list', self.current_user_settings_item_display_list)

    def save_subreddit_settings_dialog(self):
        self.settings.setValue('subreddit_content_icons_full_width', self.subreddit_content_icons_full_width)
        self.settings.setValue('subreddit_content_icon_size', self.subreddit_content_icon_size)

    def save_user_finder(self):
        self.settings.setValue("user_finder_GUI_geometry", self.user_finder_GUI_geom)
        self.settings.setValue("sub_watchlist", self.user_finder_subreddit_watchlist)
        self.settings.setValue("user_blacklist", self.user_finder_user_blacklist)
        self.settings.setValue("user_finder_sort_method", self.user_finder_sort_method)
        self.settings.setValue("user_finder_watchlist_score_limit", self.user_finder_watch_list_score_limit)
        self.settings.setValue("user_finder_watchlist_sample_size", self.user_finder_download_sample_size)
        self.settings.setValue("user_finder_run_with_main", self.user_finder_run_with_main)
        self.settings.setValue("user_finder_auto_add_users", self.user_finder_auto_add_users)
        self.settings.setValue("user_finder_add_to_index", self.user_finder_add_to_index)
        self.settings.setValue("user_finder_content_list_icons_full_size", self.user_finder_content_list_icons_full_width)
        self.settings.setValue("user_finder_content_list_icon_size", self.user_finder_content_list_icon_size)

    def save_add_user_dialog(self):
        self.settings.setValue("add_user_dialog_geom", self.add_user_dialog_geom)

    def save_failed_downloads_dialog(self):
        self.settings.setValue("failed_downloads_dialog_geom", self.failed_downloads_dialog_geom)

    def save_about_dialog(self):
        self.settings.setValue("about_dialog_geom", self.about_dialog_geom)

    def save_update_dialog(self):
        self.settings.setValue("do_not_notify_update", self.do_not_notify_update)
        self.settings.setValue("update_dialog_geom", self.update_dialog_geom)
