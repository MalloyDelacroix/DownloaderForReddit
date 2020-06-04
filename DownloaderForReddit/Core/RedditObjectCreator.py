import logging
from sqlalchemy import func

from ..Database import User, Subreddit, RedditObjectList
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

    def create_reddit_object(self, name, list_defaults):
        if self.list_type == 'USER':
            return self.create_user(name, list_defaults)
        else:
            return self.create_subreddit(name, list_defaults)

    def create_user(self, user_name, list_defaults):
        with self.db.get_scoped_session() as session:
            user = session.query(User).filter(func.lower(User.name) == user_name.lower()).first()
            if user is None:
                validation_set = self.get_name_checker().check_user_name(user_name)
                if validation_set.valid:
                    list_defaults['significant'] = True
                    user = User(name=validation_set.name, date_created=validation_set.date_created, **list_defaults)
                    session.add(user)
                    session.commit()
                    return user.id
            if user is not None:
                return user.id
            return None

    def create_subreddit(self, sub_name, list_defaults):
        with self.db.get_scoped_session() as session:
            subreddit = session.query(Subreddit).filter(func.lower(Subreddit.name) == sub_name.lower()).first()
            if subreddit is None:
                validation_set = self.get_name_checker().check_subreddit_name(sub_name)
                if validation_set.valid:
                    list_defaults['significant'] = True
                    subreddit = \
                        Subreddit(name=validation_set.name, date_created=validation_set.date_created, **list_defaults)
                    session.add(subreddit)
                    session.commit()
                    return subreddit.id
            if subreddit is not None:
                return subreddit.id
            return None

    def create_reddit_object_list(self, name, commit=True):
        with self.db.get_scoped_session() as session:
            exists = session.query(RedditObjectList.id)\
                     .filter(RedditObjectList.name == name)\
                     .filter(RedditObjectList.list_type == self.list_type)\
                     .scalar() is not None
            if not exists:
                defaults = self.get_default_setup(self.list_type)
                ro_list = RedditObjectList(name=name, list_type=self.list_type, **defaults)
                if commit:
                    session.add(ro_list)
                    session.commit()
                return ro_list
        return None

    def get_default_setup(self, object_type):
        if object_type == 'USER':
            return self.settings_manager.user_download_defaults
        else:
            return self.settings_manager.subreddit_download_defaults
