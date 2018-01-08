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


from queue import Queue

import praw
import prawcore
from PyQt5.QtCore import QObject, pyqtSignal

from Core.RedditObjects import User
from version import __version__


class UserFinder(QObject):

    remove_invalid_subreddit = pyqtSignal(object)
    step_complete = pyqtSignal()
    steps = pyqtSignal(int)
    finished = pyqtSignal()
    update_output = pyqtSignal(str)
    user_found = pyqtSignal(object)

    def __init__(self, sub_list, black_list, top_sort_method, score_limit, sample_size, existing_users, save_path,
                 imgur_client, previously_found):
        """
        A class that searches supplied subreddits for top posts (of the user set period) and collects the names of users
        who have submitted posts that scored above the set score limit.  It will then download the user specified sample
        size of posts and display them on the second page.  Also has methods to add any found users to the main download
        users list as well as methods to exclude certain users that the user wishes not to include.  Parts of this class
        work similar to the parts of the main program, but on a smaller scale.  For instance, when a user is found an
        instance of the User class is created for them with preset settings supplied.  This class is only used
        temporarily and if the user is added to the main list the instance is destroyed and a new instance made with the
        proper overall settings.

        :param sub_list: The sub list supplied by the UserFinderGUI which is to be searched for top posts
        :param black_list: A list of users who are not to be included even if their posts reach the score limit
        :param top_sort_method: The period of top posts to be searched (eg: day, week, etc.)
        :param score_limit: The limit that post scores must be above to be considered
        :param sample_size: The number of posts that are to be downloaded if the conditions are met
        :param existing_users: A list of users already added to the main GUI lists that will be emitted from search
        :param save_path: The save path of the special UserFinder directory where the user finder posts are stored
        :param imgur_client: An instance of the imgure client that is supplied to temporarily created users
        :param previously_found: A list of users that have been previously found and will not be included in the search
        """
        super().__init__()
        self._r = praw.Reddit(user_agent='python:DownloaderForReddit:%s (by /u/MalloyDelacroix)' % __version__,
                              client_id='frGEUVAuHGL2PQ', client_secret=None)
        self.sub_list = sub_list
        self.black_list = black_list
        self.top_sort_method = top_sort_method
        self.score_limit = score_limit
        self.sample_size = sample_size
        self.existing_users = existing_users
        self.save_path = save_path
        self.imgur_client = imgur_client
        self.previously_found_users = previously_found
        self.validated_subreddits = []
        self.found_users = []
        self.queue = Queue()
        self.content_count = 0

    def validate_subreddits(self):
        """Checks the supplied subreddits and makes sure they exist"""
        self.update_output.emit('Validating\n')
        self.steps.emit(len(self.sub_list))
        for sub in self.sub_list:  # This will be a ListModelObject
            subreddit = self._r.subreddit(sub)
            try:
                test = subreddit.fullname
                x = Sub(sub)
                self.validated_subreddits.append(x)
                submissions = self.get_subreddit_submissions(subreddit)
                x.get_submissions(submissions)
                self.update_output.emit('%s is valid' % sub)
                self.step_complete.emit()
            except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound):
                self.remove_invalid_subreddit.emit(sub)
                self.update_output.emit('%s is not valid' % sub)
                self.step_complete.emit()
        self.find_users()
        self.finished.emit()

    def find_users(self):
        """Finds the users which meet the search criteria"""
        self.update_output.emit('Finding Users\n')
        for sub in self.validated_subreddits:
            for post in sub.new_submissions:
                if post.score > self.score_limit:
                    name = post.author
                    if not any(name == x.name for x in self.found_users) and \
                        name not in self.existing_users and name not in self.black_list and name not in \
                            self.previously_found_users:
                        x = User(str(name), '%sUserFinder/' % self.save_path, self.imgur_client, self.sample_size,
                                 name_downloads_by='Post Title', avoid_duplicates=True, download_videos=False,
                                 download_images=True, user_added=None)
                        if x not in self.found_users:
                            self.update_output.emit('User Found: %s' % name)
                            self.user_found.emit(x)
                            self.found_users.append(x)

    def get_subreddit_submissions(self, subreddit):
        if self.top_sort_method == 0:
            submissions = [x for x in subreddit.top('hour', limit=100) if not x.is_self and x.score > self.score_limit]
        elif self.top_sort_method == 1:
            submissions = [x for x in subreddit.top('day', limit=100) if not x.is_self and x.score > self.score_limit]
        elif self.top_sort_method == 2:
            submissions = [x for x in subreddit.top('week', limit=100) if not x.is_self and x.score > self.score_limit]
        elif self.top_sort_method == 3:
            submissions = [x for x in subreddit.top('month', limit=100) if not x.is_self and x.score > self.score_limit]
        elif self.top_sort_method == 4:
            submissions = [x for x in subreddit.top('year', limit=100) if not x.is_self and x.score > self.score_limit]
        else:
            submissions = [x for x in subreddit.top('all', limit=100) if not x.is_self and x.score > self.score_limit]
        return submissions


class Sub(object):

    def __init__(self, name):
        """
        A simplified version of the larger Subreddit class.  This class is only used for the user finder portion of the
        application
        :param name: The name of the subreddit
        """
        self.name = name
        self.new_submissions = None

    def get_submissions(self, submissions):
        self.new_submissions = submissions
