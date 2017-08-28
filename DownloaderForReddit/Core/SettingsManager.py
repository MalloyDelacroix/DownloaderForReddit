import os

from PyQt5.QtCore import QSettings
import shelve

from Core.ListModel import ListModel


class SettingsManager:

    def __init__(self):
        self.settings = QSettings('SomeGuySoftware', 'RedditDownloader')
        self.load_settings()
        self.count = 0

    def load_settings(self):
        # region Core Settings
        self.first_run = self.settings.value('first_run', True, type=bool)
        self.last_update = self.settings.value('last_update', None, type=str)
        self.total_files_downloaded = self.settings.value('total_files_downloaded', 0, type=int)
        self.imgur_client = self.settings.value('imgur_client', (None, None), type=tuple)
        self.reddit_username = self.settings.value('reddit_username', None, type=str)
        self.reddit_password = self.settings.value('reddit_password', None, type=str)
        self.auto_save_on_close = self.settings.value('auto_save_on_close', False, type=bool)
        self.run_user_finder_auto = self.settings.value('run_user_finder_auto', False, type=bool)
        self.auto_display_failed_list = self.settings.value("auto_display_failed_list", True, type=bool)

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

        self.max_download_thread_count = self.settings.value('max_download_thread_count', 4, type=int)
        # endregion

        # region Main Window GUI Settings
        self.main_window_geom = self.settings.value('window_geometry')
        self.list_sort_method = self.settings.value('list__sort_method', 0, type=int)
        self.list_order_method = self.settings.value('list_order_method', 0, type=int)
        self.download_users = self.settings.value("download_users", False, type=bool)
        self.download_subreddits = self.settings.value("download_subreddits", False, type=bool)
        # endregion

        # region UserSettingsDialog Settings
        self.user_settings_dialog_geom = self.settings.value('user_settings_dialog_geometry')
        self.user_content_icons_full_width = self.settings.value('user_content_icons_full_width', False, type=bool)
        self.user_content_icon_size = self.settings.value('user_content_icon_size', 110, type=int)
        self.current_user_settings_item_display_list = self.settings.value('current_item_display_list',
                                                                           'previous_downloads', type=str)
        # endregion

        # region SubredditSettingsDialog Settings
        self.subreddit_content_icons_full_width = self.settings.value('subreddit_content_icons_full_width', False,
                                                                      type=bool)
        self.subreddit_content_icon_size = self.settings.value('subreddit_content_icon_size', 110, type=int)
        # endregion

        # region UserFinder GUI Settings
        self.user_finder_GUI_geom = self.settings.value('user_finder_GUI_geometry')
        self.subreddit_watchlist = self.settings.value('sub_watchlist', ['filler'], type=str)
        self.user_blacklist = self.settings.value('user_blacklist', ['filler'], type=str)

        self.subreddit_watchlist.remove('filler') if 'filler' in self.subreddit_watchlist else None
        self.user_blacklist.remove('filler') if 'filler' in self.user_blacklist else None

        self.user_finder_sort_type = self.settings.value("user_finder_sort_type", )
        # endregion


    def save_settings(self):
        self.settings.setValue('imgur_client', self.imgur_client)
        self.settings.setValue('reddit_username', self.reddit_username)
        self.settings.setValue('reddit_password', self.reddit_password)
        self.settings.setValue('auto_save_on_close', self.auto_save_on_close)

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

        self.settings.setValue('download_users_checkbox', self.download_users_checkbox.checkState())
        self.settings.setValue('download_subreddit_checkbox', self.download_subreddit_checkbox.checkState())

        self.settings.setValue('restrict_by_custom_date', self.restrict_by_custom_date)
        self.settings.setValue('custom__date', self.custom_date)

        self.settings.setValue('max_download_thread_count', self.max_download_thread_count)

        self.settings.setValue('list__sort_method', self.list_sort_method)
        self.settings.setValue('list_order_method', self.list_order_method)

    def load_pickeled_state(self):
        """Attempts to load the user and subreddit list from the pickled state and returns a list of the items loaded"""
        user_view_chooser_dict = {}
        subreddit_view_chooser_dict = {}
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
                    user_view_chooser_dict[x.name] = x

                for name, subreddit_list in subreddit_list_models.items():
                    x = ListModel(name, 'subreddit')
                    x.reddit_object_list = subreddit_list
                    x.display_list = [i.name for i in subreddit_list]
                    subreddit_view_chooser_dict[x.name] = x

                return [user_view_chooser_dict, subreddit_view_chooser_dict, last_user_view, last_subreddit_view]

            except KeyError:
                pass

    def save_pickle_state(self, user_list_models, subreddit_list_models, current_user_view, current_subreddit_view):
        try:
            with shelve.open("save_file", "c") as shelf:
                shelf['user_list_models'] = user_list_models
                shelf['subreddit_list_models'] = subreddit_list_models
                shelf['current_user_view'] = current_user_view
                shelf['current_subreddit_view'] = current_subreddit_view
                return True
        except:
            return False

    def save_all(self):
        self.save_core_settings()
        self.save_main_window()
        self.save_user_settings_dialog()
        self.save_subreddit_settings_dialog()

    def save_core_settings(self):
        self.settings.setValue("run_user_finder_auto", self.run_user_finder_auto)
        self.settings.setValue('auto_display_failed_list', self.auto_display_failed_list)

    def save_main_window(self):
        self.settings.setValue("window_geometry", self.main_window_geom)
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



