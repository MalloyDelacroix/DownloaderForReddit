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
        self.download_on_add = self.get('core', 'download_on_add', False)
        self.lock_reddit_object_settings = self.get('core', 'lock_reddit_object_settings', False)
        self.short_title_char_length = self.get('core', 'short_title_char_length', 15)
        # endregion

        # region Download Defaults
        self.post_limit = self.get('download_defaults', 'post_limit', 25)
        self.post_score_limit_operator = self.get('download_defaults', 'post_score_limit_operator', 0,
                                                  container=LimitOperator)
        self.post_score_limit = self.get('download_defaults', 'post_score_limit', 1000)
        self.avoid_duplicates = self.get('download_defaults', 'avoid_duplicates', True)
        self.extract_self_post_links = self.get('download_defaults', 'extract_self_post_links', False)
        self.download_self_post_text = self.get('download_defaults', 'download_self_post_text', False)
        self.self_post_file_format = self.get('download_defaults', 'self_post_file_format', 'txt')
        self.comment_file_format = self.get('download_defaults', 'comment_file_format', 'txt')
        self.download_videos = self.get('download_defaults', 'download_videos', True)
        self.download_images = self.get('download_defaults', 'download_images', True)
        self.download_gifs = self.get('download_defaults', 'download_gifs', True)
        self.download_nsfw = self.get('download_defaults', 'download_nsfw', 0, container=NsfwFilter)
        self.extract_comments = self.get('download_defaults', 'extract_comments', 2, container=CommentDownload)
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
        self.user_post_download_naming_method = self.get('download_defaults', 'user_post_download_naming_method',
                                                         '%[title]')
        self.user_comment_download_naming_method = self.get('download_defaults', 'user_comment_download_naming_method',
                                                            '%[author_name]-comment')
        self.subreddit_post_download_naming_method = self.get('download_defaults',
                                                              'subreddit_post_download_naming_method',
                                                              '%[title]')
        self.subreddit_comment_download_naming_method = self.get('download_defaults',
                                                                 'subreddit_comment_download_naming_method',
                                                                 '%[author_name]-comment')
        self.user_post_save_structure = self.get('download_defaults', 'user_post_save_structure', '%[author_name]')
        self.user_comment_save_structure = self.get('download_defaults', 'user_comment_save_structure',
                                                    'Comments/%[post_id]')
        self.subreddit_post_save_structure = self.get('download_defaults', 'subreddit_post_save_structure',
                                                      '%[subreddit_name]')
        self.subreddit_comment_save_structure = self.get('download_defaults', 'subreddit_comment_save_structure',
                                                         'Comments/%[post_id]')
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
        main_window_geom = {
            'width': 1138,
            'height': 570,
            'x': 0,
            'y': 0
        }
        self.main_window_geom = self.get('main_window_gui', 'main_window_geom', main_window_geom)
        self.horizontal_splitter_state = self.get('main_window_gui', 'horizontal_splitter_state', [228, 258, 624])
        self.list_sort_method = self.get('main_window_gui', 'list_sort_method', 2)
        self.list_order_method = self.get('main_window_gui', 'list_order_method', 2)
        self.download_radio_state = self.get('main_window_gui', 'download_radio_state', 'USER')
        # endregion

        # region Reddit Object Settings Dialog
        ro_settings_geom = {
            'width': 773,
            'height': 877,
            'x': 0,
            'y': 0
        }
        self.reddit_object_settings_dialog_geom = self.get('reddit_object_settings_dialog',
                                                           'reddit_object_settings_dialog_geom', ro_settings_geom)
        self.reddit_object_settings_dialog_splitter_state = self.get('reddit_object_settings_dialog',
                                                                     'reddit_object_settings_dialog_splitter_state',
                                                                     [181, 565])
        # endregion

        # region Download Sessions Dialog
        download_session_dialog_geom = {
            'width': 1690,
            'height': 920,
            'x': 0,
            'y': 0
        }
        self.dls_dialog_geom = self.get('download_session_dialog', 'dls_dialog_geom',
                                        download_session_dialog_geom)
        self.dls_dialog_show_reddit_objects = self.get('download_session_dialog', 'dls_dialog_show_reddit_objects',
                                                       True)
        self.dls_dialog_show_posts = self.get('download_session_dialog', 'dls_dialog_show_posts', True)
        self.dls_dialog_show_content = self.get('download_session_dialog', 'dls_dialog_show_content', True)
        self.dls_dialog_show_comments = self.get('download_session_dialog', 'dls_dialog_show_comments', True)
        self.dls_dialog_splitter_position = self.get('download_session_dialog', 'dls_dialog_splitter_position',
                                                     [330, 330, 330, 330, 330])
        self.dls_dialog_post_text_font = self.get('download_session_dialog', 'dls_dialog_post_text_font', 'Times')
        self.dls_dialog_post_text_font_size = self.get('download_session_dialog', 'dls_dialog_post_text_font_size', 10)
        self.dls_dialog_icon_size = self.get('download_session_dialog', 'dls_dialog_icon_size', 250)
        self.default_dls_post_headers = {
            'title': True,
            'date_posted_display': True,
            'score_display': True,
            'is_self': True,
            'text': True,
            'url': True,
            'domain': True,
            'author': True,
            'subreddit': True,
            'nsfw': True
        }
        self.dls_post_table_headers = self.get('download_session_dialog', 'dls_post_table_headers',
                                               self.default_dls_post_headers)
        self.default_dls_comment_headers = {
            'author': True,
            'id': False,
            'body': True,
            'body_html': False,
            'score': True,
            'subreddit': False,
            'reddit_id': False,
            'date_posted': True,
        }
        self.dls_comment_tree_headers = self.get('download_session_dialog', 'dls_comment_tree_headers',
                                                 self.default_dls_comment_headers)
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
            'download_nsfw': False,
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
