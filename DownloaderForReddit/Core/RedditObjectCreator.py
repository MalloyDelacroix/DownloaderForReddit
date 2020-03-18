from datetime import datetime
import logging
from sqlalchemy import func

from ..Database.Models import User, Subreddit
from ..Utils import Injector, RedditUtils


class RedditObjectCreator:

    def __init__(self):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.name_checker = None

    def get_name_checker(self):
        """
        Initializes the name checker, sets it to a class variable, and returns it to the caller.  This is done so that
        the name checker does not always have to be initialized if it is not needed to create the reddit object.
        :return:
        """
        self.name_checker = RedditUtils.NameChecker(None, None)
        return self.name_checker

    def create_user(self, user_name, validate=True, **kwargs):
        with self.db.get_scoped_session() as session:
            user = session.query(User).filter(func.lower(User.name) == func.lower(user_name)).first()
            if user is None:
                if validate:
                    actual_name, valid = self.get_name_checker().check_user_name(user_name)
                else:
                    actual_name = user_name
                    valid = True
                if valid:
                    defaults = self.get_default_setup('USER')
                    for key, value in kwargs.items():
                        defaults[key] = value
                    user = User(name=actual_name, **defaults)
                    session.add(user)
                    session.commit()
            return user

    def create_subreddit(self, sub_name, validate=True, **kwargs):
        with self.db.get_scoped_session() as session:
            subreddit = session.query(Subreddit).filter(func.lower(Subreddit.name) == func.lower(sub_name)).first()
            if subreddit is None:
                if validate:
                    actual_name, valid = self.get_name_checker().check_subreddit_name(sub_name)
                else:
                    actual_name = sub_name
                    valid = True
                if valid:
                    defaults = self.get_default_setup('SUBREDDIT')
                    for key, value in kwargs.items():
                        defaults[key] = value
                    subreddit = Subreddit(name=actual_name, **defaults)
                    session.add(subreddit)
                    session.commit()
            return subreddit

    def get_default_setup(self, object_type):
        defaults = {
            'post_limit': self.settings_manager.post_limit,
            'post_score_limit_operator': self.settings_manager.post_score_limit_operator,
            'post_score_limit': self.settings_manager.post_score_limit,
            'avoid_duplicates': self.settings_manager.avoid_duplicates,
            'download_videos': self.settings_manager.download_videos,
            'download_images': self.settings_manager.download_images,
            'download_comments': self.settings_manager.download_comments,
            'download_comment_content': self.settings_manager.download_comment_content,
            'download_nsfw': self.settings_manager.download_nsfw,
            'date_limit': self.settings_manager.date_limit,
            'significant': True,
            'subreddit_save_structure': self.settings_manager.subreddit_save_structure
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
