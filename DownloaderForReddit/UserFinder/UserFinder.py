from PyQt5.QtCore import QObject, pyqtSignal

from Core import Injector
from UserFinder.UserFinderRedditObject import UserFinderUser, UserFinderSubreddit
from Core.PostFilter import PostFilter


class UserFinder(QObject):

    send_user = pyqtSignal(object)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, subreddit_list, user_blacklist, user_view_chooser_dict):
        super().__init__()
        self.settings_manager = Injector.get_settings_manager()
        self._r = self.settings_manager.r
        self.post_filter = PostFilter()
        self.subreddit_list = subreddit_list
        self.blacklist = user_blacklist
        self.user_view_chooser_dict = user_view_chooser_dict

        self.valid_subreddit_list = []
        self.user_name_list = []
        self.valid_user_list = []

    def run(self):
        self.validate_subreddits()
        print('Sub Post Count: %s' % len(self.valid_subreddit_list[0].extracted_post_dict))
        self.extract_users()
        self.extract_user_content()
        self.finished.emit()

    def validate_subreddits(self):
        for item in self.subreddit_list:
            # try:
            subreddit = self._r.subreddit(item)
            sub = UserFinderSubreddit(None, item, None, self.settings_manager.user_finder_post_limit, True,
                                      self.settings_manager.download_videos, self.settings_manager.download_images,
                                      self.settings_manager.nsfw_filter, None,
                                      self.settings_manager.name_downloads_by, None)
            sub.new_submissions = [x for x in self.extract_subreddit_posts(subreddit) if self.filter_post(x)]
            sub.consolidate_posts()
            self.valid_subreddit_list.append(sub)
            # except:
            #     print('%s invalid' % item)
            #     # TODO: Make an alert for invalid subreddit

    def extract_users(self):
        """
        Extracts user names from validated subreddits and adds the names to the user names list.
        """
        for sub in self.valid_subreddit_list:
            for key, value in sub.extracted_post_dict.items():
                if self.filter_users(key):
                    user = self.check_user_list(key)
                    if not user:
                        self.make_and_add_user(key, value)
                    else:
                        self.add_posts_to_user(user, value)

    def extract_user_content(self):
        """
        Calls each users extract_content method to extract (in this case) linkable content objects that can be displayed
        in the UserFinderGUI and then emits a signal with the user object so that it can be displayed.
        """
        for user in self.valid_user_list:
            user.extract_content()
            self.send_user.emit(user)

    def filter_users(self, name):
        """
        Checks the blacklist and each user object in the user_view_chooser_dict for a match to the supplied name.
        :param name: The name that is searched for.
        :type name: str
        :return: False if a match is found, True otherwise
        :rtype: bool
        """
        if name in self.blacklist:
            return False
        for value in self.user_view_chooser_dict.values():
            for user in value.reddit_object_list:
                if user.name.lower() == name.lower():
                    return False
        return True

    def check_user_list(self, name):
        """
        Checks the valid user list for users with the supplied name and returns the user object if a match is found.
        :param name: The name for which a match is searched for from the valid user list.
        :type name: str
        :return: A UserFinderUser object with the supplied name if a match is found, None if no match is found.
        :rtype: UserFinderUser
        """
        for user in self.valid_user_list:
            if name.lower() == user.name.lower():
                return user
        return None

    def make_and_add_user(self, name, selected_posts):
        """
        Validates the supplied name, makes a UserFinderUser object from the supplied name, adds the selected posts to
        the users new submissions list, then extracts the users posts from reddit based on the user finder settings
        criteria.
        :param redditor: A praw redditor object from which the UserFinderUser object is made and the posts extracted.
        :param selected_posts: A list of the posts that were in the top posts of the searched subreddits that belong to
                               the supplied user name.
        :type redditor: Praw.Redditor
        :type selected_posts: list
        """
        # try:
        redditor = self._r.redditor(name)
        user = UserFinderUser(None, name, None, self.settings_manager.user_finder_post_limit, True,
                              self.settings_manager.download_videos, self.settings_manager.download_images,
                              self.settings_manager.nsfw_filter, self.settings_manager.name_downloads_by, None)
        self.add_selected_posts(user, selected_posts)
        posts = self.extract_user_pots(redditor)
        self.add_posts_to_user(user, posts)
        self.valid_user_list.append(user)
        # except:
        #     pass

    def add_selected_posts(self, user, selected_posts):
        """
        Adds the supplied selected posts to the supplied user.  A check is done to make sure the user object has a
        new submissions list before the selected posts are added.
        :param user: The user that the selected posts are to be added to.
        :param selected_posts: A list of selected posts to be added to the supplied user.
        :type user: UserFinderUser
        :type selected_posts: list
        """
        if self.settings_manager.user_finder_sample_type_method.startswith('SELECTED'):
            if user.new_submissions is None:
                user.new_submissions = selected_posts
            else:
                self.add_posts_to_user(user, selected_posts)

    def add_posts_to_user(self, user, posts):
        """
        Adds the supplied posts to the supplied user if the posts filter conditions are met and the post does not
        already exist in the users new submissions list.
        :param user: The user object to which the posts are added.
        :param posts: A list of posts that are to be added to the supplied user.
        :type user: UserFinderUser
        :type posts: list
        """
        filtered_posts = [x for x in posts if self.filter_nsfw(x) and self.filter_existing(user, x)]
        if user.new_submissions:
            user.new_submissions.extend(filtered_posts)
        else:
            user.new_submissions = filtered_posts

    def extract_subreddit_posts(self, subreddit):
        """
        Extracts posts from the supplied subreddit object.
        :param subreddit: The praw subreddit object that posts are to be extracted from
        :type subreddit: Praw Subreddit
        """
        return subreddit.top(self.settings_manager.user_finder_top_sort_method.lower(),
                             limit=self.settings_manager.user_finder_post_limit)

    def extract_user_pots(self, redditor):
        """
        Extracts posts from the supplied user based on the user finder settings in the settings manager.
        :param redditor: The user whos posts are to be extracted.
        :type redditor: Praw.Redditor
        :return: A list of the users posts.
        :rtype: list
        """
        post_limit = self.settings_manager.user_finder_sample_size
        method = self.settings_manager.user_finder_sample_type_method
        # print('Redditor Type: %s\nPost Limit: %s\nMethod: %s' % (type(redditor), post_limit, method))
        if method == 'TOP' or method == 'SELECTED_TOP':
            return redditor.submissions.top(limit=post_limit)
        elif method == 'NEW' or method == 'SELECTED_NEW':
            return redditor.submissions.new(limit=post_limit)

    def filter_post(self, post):
        return self.filter_score(post) and self.filter_nsfw(post)

    def filter_score(self, post):
        if self.settings_manager.user_finder_filter_by_score:
            return post.score >= self.settings_manager.user_finder_score_limit
        else:
            return True

    def filter_nsfw(self, post):
        if self.settings_manager.nsfw_filter == 'EXCLUDE':
            return not post.over_18
        elif self.settings_manager.nsfw_filter == 'ONLY':
            return post.over_18
        else:
            return True

    def filter_existing(self, user, post):
        if user.new_submissions:
            for item in user.new_submissions:
                if item.title == post.title:
                    return False
        return True








































