import os
import shelve

from Core.ListModel import ListModel


class ObjectLoader:

    def __init__(self):
        pass

    def load_pickled_state(self):
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
        print('Pickle loaded')
        return {'user_dict': user_view_chooser_dict, 'sub_dict': subreddit_view_chooser_dict,
                'last_user_view': last_user_view, 'last_sub_view': last_subreddit_view}

    def save_pickled_state(self):
        pass





































