from PyQt5.QtCore import QObject, pyqtSignal

from Core import Injector
from UserFinder.UserFinderUserObject import UserFinderUserObject
from Core.PostFilter import PostFilter


class UserFinder(QObject):

    send_user = pyqtSignal(object)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar = pyqtSignal()

    def __init__(self, subreddit_list, user_blacklist, user_view_chooser_dict):
        super().__init__()
        self.settings_manager = Injector.get_settings_manager()
        self._r = self.settings_manager.r
        self.post_filter = PostFilter()
        self.subreddit_list = subreddit_list
        self.blacklist = user_blacklist
        self.user_view_chooser_dict = user_view_chooser_dict

        self.valid_subreddit_list = []
        self.user_list = []

    def validate_subreddits(self):
        for item in self.subreddit_list:
            try:
                subreddit = self._r.subreddit(item)
                sub = UserFinderUserObject(subreddit.name)
                sub.submissions = [post for post in self.extract_subreddit_posts(subreddit) if self.filter_post(post)]
                self.valid_subreddit_list.append(sub)
            except:
                pass
                # TODO: Make an alert for invalid subreddit

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

    def extract_users(self):
        for sub in self.valid_subreddit_list:
            for post in sub.submissions:
                author = post.author

    def validate_user(self, user):
        try:
            redditor = self._r.redditor(user)
            user = UserFinderUserObject(redditor.name)
            user.total_karma = redditor.link_karma
        except:
            pass
            # TODO: make an alert for invalid redditor

    def extract_subreddit_posts(self, subreddit):
        """
        Extracts posts from the supplied subreddit object.
        :param subreddit: The praw subreddit object that posts are to be extracted from
        :type subreddit: Praw Subreddit
        """
        return subreddit.submissions.top(self.settings_manager.user_finder_top_sort_method.lower(),
                                         self.settings_manager.user_finder_post_limit)

    def extract_user_pots(self, user):
        limit = self.settings_manager.user_finder_sample_size
        if self.settings_manager.user_finder_sample_type_method == 'TOP':
            return user.submissions.top(limit)
        else:
            return user.submissions.new(limit)












































