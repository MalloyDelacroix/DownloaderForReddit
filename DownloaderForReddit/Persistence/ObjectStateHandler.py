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


import shelve
import os
import logging

from ..ViewModels.ListModel import ListModel
from ..Persistence.ObjectUpdater import ObjectUpdater
from ..Utils import SystemUtil
from ..version import __version__


class ObjectStateHandler:

    """
    A class that is responsible for saving and loading the reddit object lists.
    """

    logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
    total_user_count = 0
    total_sub_count = 0
    user_update_count = 0
    sub_update_count = 0

    @classmethod
    def load_pickled_state(cls):
        """
        Loads the reddit object lists from a pickled states and packs them into the view_chooser_dicts that they will
        be used in.
        :return: A dict of view chooser dicts and a string representing which value should be displayed currently.
        :rtype: dict
        """
        save_path = None
        try:
            user_view_chooser_dict = {}
            subreddit_view_chooser_dict = {}
            save_path = cls.get_save_path()
            with shelve.open(save_path, 'c') as shelf:
                user_list_models = shelf['user_list_models']
                subreddit_list_models = shelf['subreddit_list_models']
                last_user_view = shelf['current_user_view']
                last_subreddit_view = shelf['current_subreddit_view']

                for name, user_list in user_list_models.items():
                    user_list = cls.check_user_objects(user_list)
                    x = ListModel(name, 'user')
                    x.reddit_object_list = user_list
                    user_view_chooser_dict[x.name] = x
                    cls.total_user_count += len(user_list)

                for name, sub_list in subreddit_list_models.items():
                    sub_list = cls.check_subreddit_objects(sub_list)
                    x = ListModel(name, 'subreddit')
                    x.reddit_object_list = sub_list
                    subreddit_view_chooser_dict[name] = x
                    cls.total_sub_count += len(sub_list)
            cls.logger.info('Object lists loaded from save file', extra={'total_users': cls.total_user_count,
                                                                         'total_subreddits': cls.total_sub_count,
                                                                         'updated_users': cls.user_update_count,
                                                                         'updated_subreddits': cls.sub_update_count})
            return {'user_dict': user_view_chooser_dict, 'sub_dict': subreddit_view_chooser_dict,
                    'last_user_view': last_user_view, 'last_sub_view': last_subreddit_view}
        except KeyError:
            cls.logger.error('Failed to load from save file', extra={'save_file_location': save_path}, exc_info=True)
        except FileNotFoundError:
            cls.logger.error('Failed to load from save file: No save file found',
                             extra={'save_file_location': save_path}, exc_info=True)
            return False
        except Exception:
            cls.logger.error('Failed to load from save file', extra={'save_file_location': save_path}, exc_info=True)
            return False

    @classmethod
    def get_save_path(cls):
        """
        Builds and returns a path to the save_file based on the users OS.
        :return: The save_file path location.
        :rtype: str
        """
        return os.path.join(SystemUtil.get_data_directory(), 'save_file')

    @classmethod
    def save_pickled_state(cls, object_dict):
        """
        Unpacks the objects in the supplied object_dict and saves them in a pickled state to the hard drive.
        :param object_dict: A dict of view chooser dicts and strings representing which view chooser value is currently
                            displayed
        :type object_dict: dict
        :return: True if the save was successful and False if it was not.
        :rtype: bool
        """
        user_list_models = cls.get_list_models(object_dict['user_view_chooser_dict'])
        sub_list_models = cls.get_list_models(object_dict['sub_view_chooser_dict'])
        save_path = None
        try:
            save_path = cls.get_save_path()
            with shelve.open(save_path, 'c') as shelf:
                shelf['user_list_models'] = user_list_models
                shelf['subreddit_list_models'] = sub_list_models
                shelf['current_user_view'] = object_dict['current_user_view']
                shelf['current_subreddit_view'] = object_dict['current_sub_view']
            cls.logger.info('Objects successfully saved', extra={'total_users_saved': cls.total_user_count,
                                                                 'total_subreddits_saved': cls.total_sub_count})
            return True
        except Exception:
            cls.logger.error('Unable to save to save_file', extra={'save_file_location': save_path}, exc_info=True)
            return False

    @classmethod
    def get_list_models(cls, view_chooser_dict):
        """
        Iterates through the supplied view_chooser_dict and extracts the user list from each list model, packages it in
        a dict with the models name, then returns the dict to be pickled.
        :param view_chooser_dict: The view chooser dict (either user or subreddit) that is to be pickled.
        :type view_chooser_dict: dict
        :return: A dict with each view_chooser_dicts name and the reddit object list of the associated list model
        :rtype: dict
        """
        list_models = {}
        for key, value in view_chooser_dict.items():
            list_models[key] = value.reddit_object_list
            if value.list_type == 'user':
                cls.total_user_count += len(value.reddit_object_list)
            else:
                cls.total_sub_count += len(value.reddit_object_list)
        return list_models

    @classmethod
    def check_user_objects(cls, user_list):
        for index in range(len(user_list)):
            if not cls.check_version(user_list[index]):
                x = ObjectUpdater.update_user(user_list[index])
                user_list[index] = x
                cls.user_update_count += 1
        return user_list

    @classmethod
    def check_subreddit_objects(cls, sub_list):
        for index in range(len(sub_list)):
            if not cls.check_version(sub_list[index]):
                x = ObjectUpdater.update_subreddit(sub_list[index])
                sub_list[index] = x
                cls.sub_update_count += 1
        return sub_list

    @staticmethod
    def check_version(item):
        try:
            return item.version == __version__
        except AttributeError:
            return False
