import logging
from sqlalchemy import func

from ..database.models import User, Subreddit, RedditObjectList
from ..utils import injector, reddit_utils


class RedditObjectCreator:

    def __init__(self, list_type):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
        self.list_type = list_type
        self.name_checker = None

    def get_name_checker(self):
        """
        Initializes the name checker, sets it to a class variable, and returns it to the caller.  This is done so that
        the name checker does not always have to be initialized if it is not needed to create the reddit object.
        """
        if self.name_checker is None:
            self.name_checker = reddit_utils.NameChecker(self.list_type)
        return self.name_checker

    def create_reddit_object(self, name, list_defaults):
        if self.list_type == 'USER':
            return self.create_user(name, list_defaults)
        else:
            return self.create_subreddit(name, list_defaults)

    def create_user(self, user_name, list_defaults):
        """
        Takes a given user name and first searches in the database for its existence.  If it is already in the database
        the existing objects id is returned.  If it is not already in the database, the name is validated with reddit
        to ensure that it is a valid name, then a new database object is created for the user and the id is returned.
        :param user_name: The name of the User that is to be validated and created.
        :param list_defaults: A dict of default values to be used in the creation of a new User object.  These defaults
                              come from the settings of the list in which the user is being added.
        :return: A tuple in which the first value is the id of the existing or created user, and the second is a bool
                 indicating whether or not the user was created. True if the user was created, False if it was existing.
        :type user_name: str
        :type list_defaults: dict
        :rtype: tuple
        """
        with self.db.get_scoped_session() as session:
            user = session.query(User).filter(func.lower(User.name) == user_name.lower()).first()
            if user is None:
                if self.settings_manager.validate_names_before_add:
                    validation_set = self.get_name_checker().check_user_name(user_name)
                else:
                    validation_set = reddit_utils.ValidationSet(name=user_name, date_created=None, valid=True)
                if validation_set.valid:
                    list_defaults['significant'] = True
                    user = User(name=validation_set.name, date_created=validation_set.date_created, **list_defaults)
                    session.add(user)
                    session.commit()
                    return user.id, True
            if user is not None:
                return user.id, False
            return None

    def create_subreddit(self, sub_name, list_defaults):
        """See create_user above."""
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
                    return subreddit.id, True
            if subreddit is not None:
                return subreddit.id, False
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
