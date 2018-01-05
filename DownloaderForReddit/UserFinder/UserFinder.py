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


from PyQt5.QtCore import QObject, pyqtSignal
import prawcore

from Core import Injector
from UserFinder.UserFinderRedditObject import UserFinderUser, UserFinderSubreddit
from Core.PostFilter import PostFilter
from Core.Messages import Message


class UserFinder(QObject):

    send_user = pyqtSignal(object)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar = pyqtSignal()
    user_post_count_signal = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, subreddit_list, user_blacklist, user_view_chooser_dict):
        """
        A class that takes a list of subreddits and extracts each subreddits top posts based on supplied settings then
        makes a list of the users that made the posts.  The found users top or new posts are then extracted and the the
        found user is sent to be displayed

        :param subreddit_list: A list of subreddit names to be scanned.
        :param user_blacklist: A list of reddit user names that if found by the search will not be included in the found
                               list.
        :param user_view_chooser_dict: The main window view chooser dict so that existing names can be matched and
                                       excluded from the found users list.
        """
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
        """Calls the user finder methods in the necessary order."""
        self.validate_subreddits()
        self.extract_users()
        self.extract_user_content()
        self.finished.emit()

    def validate_subreddits(self):
        """
        Validates each subreddit in the subreddit list, creates a UserFinderSubreddit object if valid, extracts the
        subreddits top posts based on the user finder settings, then adds the subreddit to the valid subreddit list.
        """
        for item in self.subreddit_list:
            try:
                subreddit = self._r.subreddit(item)
                sub = UserFinderSubreddit(None, item, None, self.settings_manager.user_finder_post_limit, True,
                                          self.settings_manager.download_videos, self.settings_manager.download_images,
                                          self.settings_manager.nsfw_filter, None,
                                          self.settings_manager.name_downloads_by, None)
                sub.new_submissions = [x for x in self.extract_subreddit_posts(subreddit) if self.filter_post(x)]
                sub.consolidate_posts()
                self.valid_subreddit_list.append(sub)
            except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
                Message.subreddit_not_valid(self, item)

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
        :param name: The name of a redditor that is to be extracted.
        :param selected_posts: A list of the posts that were in the top posts of the searched subreddits that belong to
                               the supplied user name.
        :type name: str
        :type selected_posts: list
        """
        try:
            redditor = self._r.redditor(name)
            user = UserFinderUser(redditor.link_karma, redditor.created, None, name, None,
                                  self.settings_manager.user_finder_post_limit, True,
                                  self.settings_manager.download_videos, self.settings_manager.download_images,
                                  self.settings_manager.nsfw_filter, self.settings_manager.name_downloads_by, None)
            self.add_selected_posts(user, selected_posts)
            posts = self.extract_user_pots(redditor)
            self.add_posts_to_user(user, posts)
            user.last_post_date = self.get_last_post_date(redditor, user.new_submissions)
            self.valid_user_list.append(user)
        except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
            pass

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

    def get_last_post_date(self, redditor, post_list):
        """
        Gets and returns the date of the last post made by the supplied redditor.  An already extracted list of posts
        are also supplied so if the posts that have been extracted were extracted under the 'new' method, the date is
        extracted from this list so no further extraction is needed. If the extraction method is not 'new', one new post
        is extracted from the redditor and its date returned.
        :param redditor: A praw redditor object who's last post date is returned.
        :param post_list: A list of already extracted posts that are checked for a last post date.
        :return: The date of the users last post.
        """
        if 'NEW' in self.settings_manager.user_finder_sample_type_method:
            return sorted([x.created for x in post_list], reverse=True)[0]
        else:
            return [x for x in redditor.submissions.new(limit=1)][0].created

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
        if method == 'TOP' or method == 'SELECTED_TOP':
            return redditor.submissions.top(limit=post_limit)
        elif method == 'NEW' or method == 'SELECTED_NEW':
            return redditor.submissions.new(limit=post_limit)

    def filter_post(self, post):
        """
        Filters the supplied post based on the UserFinder filter settings.
        :param post: The post that is filtered.
        :return: True if the post passes the filters, False if not.
        """
        return self.filter_score(post) and self.filter_nsfw(post)

    def filter_score(self, post):
        """Checks the supplied posts score and returns whether or not it is greater than the user finder score limit."""
        if self.settings_manager.user_finder_filter_by_score:
            return post.score >= self.settings_manager.user_finder_score_limit
        else:
            return True

    def filter_nsfw(self, post):
        """
        Checks the supplied post and returns whether or not the post meets the nsfw filter settings from the
        settings manager.
        """
        if self.settings_manager.nsfw_filter == 'EXCLUDE':
            return not post.over_18
        elif self.settings_manager.nsfw_filter == 'ONLY':
            return post.over_18
        else:
            return True

    def filter_existing(self, user, post):
        """
        Checks the supplied users new_submissions list to see if the supplied post already exists in the list.
        :param user: The user object who's new_submissions list is to be checked.
        :param post: The post that is checked for prior existence.
        :type user: UserFinderUser
        :type post: praw.submission
        :return: False if the post exists in the users new_submissions list and True if it does not.
        :rtype: bool
        """
        if user.new_submissions:
            for item in user.new_submissions:
                if item.title == post.title:
                    return False
        return True

    def get_user_count(self, user):
        redditor = self._r.redditor(user)
        self.user_post_count_signal.emit((len(list(redditor.submissions.new(limit=None))), user))
        self.finished.emit()
