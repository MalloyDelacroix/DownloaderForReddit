import os
import shelve

from Core.ListModel import ListModel


class ObjectStateHandler:

    """
    A class that is responsible for saving and loading the reddit object lists.
    """

    def __init__(self):
        pass

    def load_pickled_state(self):
        """
        Loads the reddit object lists from a pickled states and packs them into the view_chooser_dicts that they will
        be used in.
        :return: A dict of view chooser dicts and a string representing which value should be displayed currently.
        :rtype: dict
        """
        user_view_chooser_dict = {}
        subreddit_view_chooser_dict = {}
        with shelve.open('save_file', 'c') as shelf:
            user_list_models = shelf['user_list_models']
            subreddit_list_models = shelf['subreddit_list_models']
            last_user_view = shelf['current_user_view']
            last_subreddit_view = shelf['current_subreddit_view']

            for name, user_list in user_list_models.items():
                x = ListModel(name, 'user')
                x.reddit_object_list = user_list
                x.display_list = [i.name for i in user_list]
                user_view_chooser_dict[x.name] = x

            for name, sub_list in subreddit_list_models.items():
                x = ListModel(name, 'subreddit')
                x.reddit_object_list = sub_list
                x.display_list = [i.name for i in sub_list]
                subreddit_view_chooser_dict[name] = x
        return {'user_dict': user_view_chooser_dict, 'sub_dict': subreddit_view_chooser_dict,
                'last_user_view': last_user_view, 'last_sub_view': last_subreddit_view}

    def save_pickled_state(self, object_dict):
        """
        Unpacks the objects in the supplied object_dict and saves them in a pickled state to the hard drive.
        :param object_dict: A dict of view chooser dicts and strings representing which view chooser value is currently
        displayed
        :type object_dict: dict
        :return: True if the save was successful and False if it was not.
        :rtype: bool
        """
        user_list_models = self.get_list_models(object_dict['user_view_chooser_dict'])
        sub_list_models = self.get_list_models(object_dict['sub_view_chooser_dict'])
        try:
            with shelve.open('save_file', 'c') as shelf:
                shelf['user_list_models'] = user_list_models
                shelf['subreddit_list_models'] = sub_list_models
                shelf['current_user_view'] = object_dict['current_user_view']
                shelf['current_subreddit_view'] = object_dict['current_sub_view']
            return True
        except:
            return False

    @staticmethod
    def get_list_models(view_chooser_dict):
        list_models = {}
        for value in view_chooser_dict.values():
            list_models[value.name] = value
        return list_models




































