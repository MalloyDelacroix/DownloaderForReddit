from Core.RedditObjects import *
from version import __version__


class ObjectUpdater:

    """
    A class that updates outdated reddit objects that have been loaded from a pickled state to a new version of the
    objects with current methods and attributes that are needed to be used in the current version of the app.
    """

    def __init__(self, user_view_chooser_dict, subreddit_view_chooser_dict):
        self.user_view_chooser_dict = user_view_chooser_dict
        self.subreddit_view_chooser_dict = subreddit_view_chooser_dict

    def update_user_objects(self):
        """
        Iterates through the list_models saved in the user_view_chooser_dict and calls the methods to update the object
        list.
        """
        for list_model in self.user_view_chooser_dict.values():
            self.update_list_model(list_model, 'USER')

    def update_subreddit_objects(self):
        """
        Iterates through the list_models saved in the subreddit_view_chooser_dict and calls the methods to update the
        object list.
        """
        for list_model in self.subreddit_view_chooser_dict.values():
            self.update_list_model(list_model, 'SUB')

    def update_list_model(self, list_model, type):
        """
        Builds a new list of updated reddit objects and replaces the supplied list models object list with the updated
        version.
        :param list_model: A list model object that holds the reddit objects to be updated.
        """
        new_object_list = []
        for item in list_model.reddit_object_list:
            if type == 'USER':
                new_object_list.append(self.update_user(item))
            else:
                new_object_list.append(self.update_subreddit(item))
        list_model.reddit_object_list = new_object_list

    def update_user(self, user):
        """
        Creates a new User object with current methods and attributes and fills in the new users attributes with
        attributes from the old user object.
        :param user: The User object which is to be updated.
        :type user: User
        """
        new_user = User(__version__, user.name, user.save_path, user.post_limit, user.avoid_duplicates,
                        user.download_videos, user.download_images, user.name_downloads_by, user.user_added)
        self.update_extras(user, new_user)
        return new_user

    def update_subreddit(self, sub):
        """
        Creates a new Subreddit object with current methods and attributes and fills in the new subs attributes with
        the attributes from the old subreddit object.
        :param sub: The outdated subreddit object wich is to be updated.
        :type sub: Subreddit
        """
        new_sub = Subreddit(__version__, sub.name, sub.save_path, sub.post_limit, sub.avoid_duplicates,
                            sub.download_videos, sub.download_images, sub.subreddit_save_method, sub.name_downloads_by,
                            sub.user_added)
        self.update_extras(sub, new_sub)
        return new_sub

    def update_extras(self, old, new):
        new.do_not_edit = old.do_not_edit
        new.date_limit = old.date_limit
        new.custom_date_limit = old.custom_date_limit
        self.get_already_downloaded(old, new)
        self.get_saved_content(old, new)
        self.get_saved_submissions(old, new)
        self.get_number_of_downloads(old, new)

    @staticmethod
    def get_already_downloaded(old, new):
        """
        Transfers the already_downloaded list from the old object to the new object.
        :param old: The old reddit object
        :param new: The new reddit object
        :type old: RedditObject
        type new: RedditObject
        """
        try:
            new.already_downloaded = old.already_downloaded
        except:
            pass

    @staticmethod
    def get_saved_content(old, new):
        """
        Transfers the saved_content list from the old object to the new object.
        :param old: The old reddit object.
        :param new: The new reddit object.
        :type old: RedditObject
        :type new: RedditObject
        """
        try:
            new.saved_content = old.saved_content
        except AttributeError:
            pass

    @staticmethod
    def get_saved_submissions(old, new):
        """
        Transfers saved submissions for previous reddit object to new reddit object.
        :param old: The old reddit object.
        :param new: The new reddit object.
        :type old: RedditObject
        :type new: RedditObject
        """
        try:
            new.saved_submissions = old.saved_submissions
        except AttributeError:
            pass

    @staticmethod
    def get_number_of_downloads(old, new):
        """
        Transfers number of downloads from previous reddit object to a new reddit object.
        :param old: The old reddit object.
        :param new: The new reddit object.
        :type old: RedditObject
        :type new: RedditObject
        """
        try:
            new.number_of_downloads = old.number_of_downloads
        except AttributeError:
            try:
                new.number_of_downloads = len(old.already_downloaded)
            except:
                pass
