import os
import toml
import logging
from datetime import datetime

from ..Utils import SystemUtil
from ..Core import Const
from ..Database.ModelEnums import *


class SettingsManager:

    def __init__(self):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.config_file_path = os.path.join(SystemUtil.get_data_directory(), 'config.toml')
        self.config = None
        self.load_config_file()
        self.section_dict = {}
        self.conversion_list = []

        # region Core
        self.last_update = self.get('core', 'last_update', Const.FIRST_POST_EPOCH)
        self.extraction_thread_count = self.get('core', 'extraction_thread_count', 4)
        self.download_thread_count = self.get('core', 'download_thread_count', 4)
        self.match_file_modified_to_post_date = self.get('core', 'match_file_modified_to_post_date', True)
        default_save_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'RedditDownloads')
        self.user_save_directory = self.get('core', 'user_save_directory', default_save_path)
        self.subreddit_save_directory = self.get('core', 'subreddit_save_directory', default_save_path)
        self.current_user_list = self.get('core', 'current_user_list', None)
        self.current_subreddit_list = self.get('core', 'current_subreddit_list', None)
        self.download_users_on_add = self.get('core', 'download_users_on_add', False)
        self.download_subreddits_on_add = self.get('core', 'download_subreddits_on_add', False)
        # endregion

        # region Download Defaults
        self.post_limit = self.get('download_defaults', 'post_limit', 25)
        self.post_score_limit_operator = self.get('download_defaults', 'post_score_limit_operator', 0,
                                                  container=LimitOperator)
        self.post_score_limit = self.get('download_defaults', 'post_score_limit', 1000)
        self.avoid_duplicates = self.get('download_defaults', 'avoid_duplicates', True)
        self.download_videos = self.get('download_defaults', 'download_videos', True)
        self.download_images = self.get('download_defaults', 'download_images', True)
        self.download_nsfw = self.get('download_defaults', 'download_nsfw', 0, container=NsfwFilter)
        self.download_comments = self.get('download_defaults', 'download_comments', 2,
                                          container=CommentDownload)
        self.download_comment_content = self.get('download_defaults', 'download_comment_content', 2,
                                                 container=CommentDownload)
        self.comment_limit = self.get('download_defaults', 'comment_limit', 100)
        self.comment_score_limit = self.get('download_defaults', 'comment_score_limit', 1000)
        self.comment_score_limit_operator = self.get('download_defaults', 'comment_score_limit_operator', 0,
                                                     container=LimitOperator)
        self.comment_sort_method = self.get('download_defaults', 'comment_sort_method', 1, container=CommentSortMethod)
        self.date_limit = self.get('download_defaults', 'date_limit', None)
        self.absolute_date_limit = self.get('download_defaults', 'absolute_date_limit',
                                            datetime.fromtimestamp(Const.FIRST_POST_EPOCH))
        self.user_post_sort_method = self.get('download_defaults', 'user_post_sort_method', 1, container=PostSortMethod)
        self.subreddit_post_sort_method = self.get('download_defaults', 'subreddit_post_sort_method', 1,
                                                   container=PostSortMethod)
        self.user_download_naming_method = self.get('download_defaults', 'user_download_naming_method', 2,
                                                    container=DownloadNameMethod)
        self.subreddit_download_naming_method = self.get('download_defaults', 'subreddit_download_naming_method', 2,
                                                         container=DownloadNameMethod)
        self.subreddit_save_structure = self.get('download_defaults', 'subreddit_save_structure', 1,
                                                 container=SubredditSaveStructure)
        self.download_reddit_hosted_videos = self.get('download_defaults', 'download_reddit_hosted_videos', True)
        # endregion

        # region Notification Defaults
        self.do_not_notify_update = self.get('notification_defaults', 'do_not_notify_update', True)
        self.auto_display_failed_downloads = self.get('notification_defaults', 'auto_display_failed_downloads', True)
        self.display_ffmpeg_warning = self.get('notification_defaults', 'display_ffmpeg_warning', True)
        # endregion

        # region Imgur
        self.imgur_client_id = self.get('imgur', 'imgur_client_id')
        self.imgur_client_secret = self.get('imgur', 'imgur_client_secret')
        self.imgur_mashape_key = self.get('imgur', 'imgur_mashape_key')
        # endregion

        # region Main Window GUI
        # self.main_window_geom = self.get('main_window_gui', 'main_window_geom')
        main_window_geom = {
            'width': 1138,
            'height': 570,
            'x': 0,
            'y': 0
        }
        self.main_window_geom = self.get('main_window_gui', 'main_window_geom', main_window_geom)
        self.horizontal_splitter_state = self.get('main_window_gui', 'horizontal_splitter_state', [47, 47])
        self.vertical_splitter_state = self.get('main_window_gui', 'vertical_splitter_state', [10, 10])
        self.list_sort_method = self.get('main_window_gui', 'list_sort_method', 2)
        self.list_order_method = self.get('main_window_gui', 'list_order_method', 2)
        self.download_users_state = self.get('main_window_gui', 'download_users_state', False)
        self.download_subreddits_state = self.get('main_window_gui', 'download_subreddits_state', False)
        # endregion

        # region Reddit Object Settings Dialog
        self.reddit_object_settings_dialog_geom = self.get('reddit_object_settings_dialog',
                                                           'reddit_object_settings_dialog_geom')
        self.reddit_object_content_icons_full_width = self.get('reddit_object_settings_dialog',
                                                               'reddit_object_content_icons_full_width', False)
        self.reddit_object_content_icon_size = self.get('reddit_object_settings_dialog',
                                                        'reddit_object_content_icon_size', 110)
        self.reddit_object_settings_dialog_splitter_state = self.get('reddit_object_settings_dialog',
                                                                     'reddit_object_settings_dialog_splitter_state')
        # endregion

        # region Misc Dialogs
        self.settings_dialog_geom = self.get('misc_dialogs', 'settings_dialog_geom')
        self.failed_downloads_dialog_geom = self.get('misc_dialogs', 'failed_downloads_dialog_geom')
        self.failed_downloads_dialog_splitter_state = self.get('misc_dialogs', 'failed_downloads_dialog_splitter_state')
        self.update_dialog_geom = self.get('misc_dialogs', 'update_dialog_geom')
        # endregion

        default_tooltip_display_dict = {
            'name': True,
            'download_enabled': True,
            'lock_settings': False,
            'last_download_date': False,
            'date_limit': True,
            'absolute_date_limit': False,
            'post_limit': False,
            'download_naming_method': False,
            'subreddit_save_method': False,
            'download_videos': False,
            'download_images': False,
            'download_comments': False,
            'download_comment_content': False,
            'nsfw_filter': False,
            'date_added': False
        }
        self.main_window_tooltip_display_dict = self.get('tooltip_display', 'main_window_tooltip_display_dict',
                                                         default_tooltip_display_dict)

    def load_config_file(self):
        try:
            self.config = toml.load(self.config_file_path)
        except:
            self.config = {
                'title': 'Downloader For Reddit configuration file',
                'warning': 'Users are free to change these values directly, but do so carefully.  Values that are '
                           'directly modified in this file and not through an application window may cause '
                           'unpredictable behavior (but most likely crashing) if the values entered are not accounted '
                           'for by the application.'
            }
            with open(self.config_file_path, 'w') as file:
                toml.dump(self.config, file)

    def save_all(self):
        for section, key_list in self.section_dict.items():
            for key in key_list:
                value = self.get_save_value(key)
                try:
                    self.config[section][key] = value
                except KeyError:
                    self.config[section] = {key: value}
        with open(self.config_file_path, 'w') as file:
            toml.dump(self.config, file)

    def get_save_value(self, key):
        value = getattr(self, key)
        if key in self.conversion_list:
            return value.value
        return value

    def get(self, section, key, default_value=None, container=None):
        """
        Attempts to extract the value from the config object that is loaded from a config file.  The default value is
        returned if the key is not found in the config.
        :param section: The section that the key is located in.
        :param key: The key to the value that is needed.
        :param default_value: The value that will be returned if the key is not found in the config object.
        :param container: Optional.  Object that should wrap the value loaded from the config file.  Since objects such
                          as ModelEnums are not able to be stored in the config file, a storable value is used instead.
                          When a container is supplied the supplied container object will be initialized with the value
                          loaded from the config file.
        :return: The value as stored in the configuration.
        """
        self.map_section(section, key)
        try:
            value = self.config[section][key]
        except KeyError:
            value = default_value
        if container is None:
            return value
        else:
            self.conversion_list.append(key)
            return container(value)

    def map_section(self, section, key):
        try:
            key_list = self.section_dict[section]
            key_list.append(key)
        except KeyError:
            self.section_dict[section] = [key]
