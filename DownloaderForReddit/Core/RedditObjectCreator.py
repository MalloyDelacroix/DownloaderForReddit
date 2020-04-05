import logging
from sqlalchemy import func

from ..Database.Models import User, Subreddit
from ..Utils import Injector, RedditUtils


class RedditObjectCreator:

    def __init__(self, list_type):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.list_type = list_type
        self.name_checker = None

    def get_name_checker(self):
        """
        Initializes the name checker, sets it to a class variable, and returns it to the caller.  This is done so that
        the name checker does not always have to be initialized if it is not needed to create the reddit object.
        """
        if self.name_checker is None:
            self.name_checker = RedditUtils.NameChecker(self.list_type)
        return self.name_checker

    def create_reddit_object(self, name, **kwargs):
        if self.list_type == 'USER':
            return self.create_user(name, **kwargs)
        else:
            return self.create_subreddit(name, **kwargs)

    def create_user(self, user_name, **kwargs):
        with self.db.get_scoped_session() as session:
            user = session.query(User).filter(func.lower(User.name) == user_name.lower()).first()
            if user is None:
                validation_set = self.get_name_checker().check_user_name(user_name)
                if validation_set.valid:
                    defaults = self.get_default_setup('USER')
                    for key, value in kwargs.items():
                        defaults[key] = value
                    user = User(name=validation_set.name, date_created=validation_set.date_created, **defaults)
                    session.add(user)
                    session.commit()
                    return user.id
            if user is not None:
                return user.id
            return None

    def create_subreddit(self, sub_name, **kwargs):
        with self.db.get_scoped_session() as session:
            subreddit = session.query(Subreddit).filter(func.lower(Subreddit.name) == sub_name.lower()).first()
            if subreddit is None:
                validation_set = self.get_name_checker().check_subreddit_name(sub_name)
                if validation_set.valid:
                    defaults = self.get_default_setup('SUBREDDIT')
                    for key, value in kwargs.items():
                        defaults[key] = value
                    subreddit = \
                        Subreddit(name=validation_set.name, date_created=validation_set.date_created, **defaults)
                    session.add(subreddit)
                    session.commit()
                    return subreddit.id
            if subreddit is not None:
                return subreddit.id
            return None

    def get_default_setup(self, object_type):
        defaults = {
            'post_limit': self.settings_manager.post_limit,
            'post_score_limit_operator': self.settings_manager.post_score_limit_operator,
            'post_score_limit': self.settings_manager.post_score_limit,
            'avoid_duplicates': self.settings_manager.avoid_duplicates,
            'extract_self_post_links': self.settings_manager.extract_self_post_links,
            'download_self_post_text': self.settings_manager.download_self_post_text,
            'self_post_file_format': self.settings_manager.self_post_file_format,
            'download_videos': self.settings_manager.download_videos,
            'download_images': self.settings_manager.download_images,
            'download_nsfw': self.settings_manager.download_nsfw,
            'download_comments': self.settings_manager.download_comments,
            'download_comment_content': self.settings_manager.download_comment_content,
            'comment_limit': self.settings_manager.comment_limit,
            'comment_score_limit': self.settings_manager.comment_score_limit,
            'comment_score_limit_operator': self.settings_manager.comment_score_limit_operator,
            'comment_sort_method': self.settings_manager.comment_sort_method,
            'date_limit': self.settings_manager.date_limit,
            'significant': True,
            'subreddit_save_structure': self.settings_manager.subreddit_save_structure,
            'lock_settings': self.settings_manager.lock_reddit_object_settings
        }
        self.get_specific_defaults(defaults, object_type)
        return defaults

    def get_specific_defaults(self, defaults, object_type):
        if object_type == 'USER':
            post_sort_method = self.settings_manager.user_post_sort_method
            download_naming_method = self.settings_manager.user_download_naming_method
        else:
            post_sort_method = self.settings_manager.subreddit_post_sort_method
            download_naming_method = self.settings_manager.subreddit_download_naming_method
        defaults.update({'post_sort_method': post_sort_method, 'download_naming_method': download_naming_method})
