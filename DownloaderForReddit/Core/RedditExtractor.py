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


import praw
import prawcore
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, QThread
from queue import Queue

import Core.Injector
from version import __version__


class RedditExtractor(QObject):

    remove_invalid_user = pyqtSignal(object)
    remove_invalid_subreddit = pyqtSignal(object)
    finished = pyqtSignal()
    downloaded_users_signal = pyqtSignal(dict)
    unfinished_downloads_signal = pyqtSignal(list)
    status_bar_update = pyqtSignal(str)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar_signal = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self, user_list, subreddit_list, queue, unfinished_downloads_list):
        """
        Class that does the main part of the work for the program.  This class contains the praw instance that is used
        for actually extracting the content from reddit.  When an instance is created all settings parameters must be
        supplied to the instance.  This class also calls the necessary functions of the other classes and completes the
        downloads.

        :param user_list: The actual list of User objects contained in the user ListModel class displayed in the GUI
        :param subreddit_list: The actual list of Subreddit objects contained in the subreddit ListModel class displayed
                               in the GUI. If this class is initialized to only run a user list, this parameter is None
        :param queue: The queue that text is added to in order to update the GUI
        The rest of teh parameters are all configuration options that are set in the settings dialog
        """
        super().__init__()
        self._r = praw.Reddit(user_agent='python:DownloaderForReddit:%s (by /u/MalloyDelacroix)' % __version__,
                              client_id='frGEUVAuHGL2PQ', client_secret=None)
        self.settings_manager = Core.Injector.get_settings_manager()
        self.user_list = user_list
        self.subreddit_list = subreddit_list
        self.queue = queue
        self.validated_objects = Queue()
        self.validated_subreddits = []
        self.failed_downloads = []
        self.downloaded_users = {}
        self.unfinished_downloads = []
        self.user_run = True if self.user_list is not None else False

        self.post_limit = self.settings_manager.post_limit
        self.save_path = self.settings_manager.save_directory
        self.subreddit_sort_method = self.settings_manager.subreddit_sort_method
        self.subreddit_sort_top_method = self.settings_manager.subreddit_sort_top_method
        self.restrict_date = self.settings_manager.restrict_by_date
        self.restrict_by_score = self.settings_manager.restrict_by_score
        self.restrict_score_method = self.settings_manager.score_limit_operator
        self.restrict_score_limit = self.settings_manager.post_score_limit
        self.unfinished_downloads_list = unfinished_downloads_list
        self.load_undownloaded_content = self.settings_manager.save_undownloaded_content

        self.queued_posts = Queue()
        self.run = True
        self.start_extractor()
        self.start_downloader()

        self.download_number = 0

    def validate_users(self):
        """Validates users and builds a list of all posts to reddit that meet the user provided criteria"""
        self.setup_progress_bar.emit(len(self.user_list) * 2)
        for user in self.user_list:
            if self.run:
                redditor = self._r.redditor(user.name)
                try:
                    test = redditor.fullname
                except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
                    redditor = None
                    self.remove_invalid_user.emit(user)

                if redditor is not None:
                    self.queue.put("%s is valid" % user.name)
                    # Sets date limit according to settings GUI
                    if not self.restrict_date:
                        date_limit = 1
                    elif user.custom_date_limit is not None:
                        date_limit = user.custom_date_limit
                    else:
                        date_limit = user.date_limit
                    submissions = self.get_submissions_user(redditor, date_limit, user.post_limit)
                    user.get_new_submissions(submissions)
                    self.validated_objects.put(user)
                    user.check_save_path()
                    self.update_progress_bar()
                else:
                    self.queue.put("%s does not exist" % user.name)
                    self.update_progress_bar()
                    self.update_progress_bar()
        self.validated_objects.put(None)

    def validate_subreddits(self):
        """See validate_users"""
        self.setup_progress_bar.emit(len(self.subreddit_list) * 2)
        for sub in self.subreddit_list:
            if self.run:
                subreddit = self._r.subreddit(sub.name)
                try:
                    test = subreddit.fullname
                except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
                    subreddit = None
                    self.remove_invalid_subreddit.emit(sub)

                if subreddit is not None:
                    self.queue.put("%s is valid" % sub.name)
                    date_limit = sub.date_limit if self.restrict_date else 1
                    submissions = self.get_submissions_subreddit(subreddit, date_limit, sub.post_limit)
                    sub.get_new_submissions(submissions)
                    self.validated_objects.put(sub)
                    sub.check_save_path()
                    self.update_progress_bar()
                else:
                    self.queue.put("%s is not a valid subreddit" % sub.name)
                    self.update_progress_bar()
                    self.update_progress_bar()
        self.validated_objects.put(None)

    def validate_users_and_subreddits(self):
        """See validate_users"""
        for sub in self.subreddit_list:
            if self.run:
                try:
                    subreddit = self._r.subreddit(sub.name)
                    self.validated_subreddits.append(subreddit.display_name)
                    self.queue.put('%s is valid' % subreddit.display_name)
                except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
                    self.queue.put('%s is not valid' % sub.name)

        if self.run:
            for user in self.user_list:
                redditor = self._r.redditor(user.name)
                try:
                    test = redditor.fullname
                except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
                    redditor = None
                    self.queue.put('%s is not valid' % user.name)
                    self.update_progress_bar()
                    self.update_progress_bar()

                if redditor is not None:
                    self.queue.put('%s is valid' % user.name)
                    submissions = [x for x in redditor.get_submitted(limit=self.post_limit) if x.created >
                                   user.date_limit and x.subreddit.display_name in self.validated_subreddits]
                    user.get_new_submissions(submissions)
                    self.validated_objects.put(user)
                    user.check_save_path()
                    self.update_progress_bar()
        self.validated_objects.put(None)

    def downloads_finished(self):
        try:
            for sub in self.subreddit_list:
                sub.clear_download_session_data()
        except TypeError:
            pass
        try:
            for user in self.user_list:
                user.clear_download_session_data()
        except TypeError:
            pass
        self.queue.put('\nFinished')
        # self.send_unfinished_downloads()
        if len(self.downloaded_users) > 0:
            self.send_downloaded_users()
        self.finished.emit()

    def start_extractor(self):
        self.extractor = Extractor(self.queue, self.validated_objects, self.queued_posts, self.user_run)
        self.stop.connect(self.extractor.stop)
        self.extractor_thread = QThread()
        self.extractor.moveToThread(self.extractor_thread)
        self.extractor_thread.started.connect(self.extractor.extract)
        self.extractor.update_progress_bar.connect(self.update_progress_bar)
        self.extractor.send_user.connect(self.add_downloaded_user)
        self.extractor.finished.connect(self.extractor_thread.quit)
        self.extractor.finished.connect(self.extractor.deleteLater)
        self.extractor_thread.finished.connect(self.extractor_thread.deleteLater)
        self.extractor_thread.start()

    def start_downloader(self):
        self.downloader = Downloader(self.queued_posts, self.settings_manager.max_download_thread_count)
        self.stop.connect(self.downloader.stop)
        self.downloader_thread = QThread()
        self.downloader.moveToThread(self.downloader_thread)
        self.downloader_thread.started.connect(self.downloader.download)
        self.downloader.finished.connect(self.downloader_thread.quit)
        self.downloader.finished.connect(self.downloader.deleteLater)
        self.downloader_thread.finished.connect(self.downloader_thread.deleteLater)
        self.downloader_thread.finished.connect(self.downloads_finished)
        self.downloader_thread.start()

    def get_submissions_user(self, user, date_limit, post_limit):  # 0 = greater than, 1 = less than
        """Extracts user submissions from reddit if they meet the user provided criteria"""
        if self.restrict_by_score and self.restrict_score_method == 0:
            submissions = [x for x in user.submissions.new(limit=post_limit) if x.created > date_limit and not
                           x.is_self and x.score > self.restrict_score_limit]
        elif self.restrict_by_score and self.restrict_score_method == 1:
            submissions = [x for x in user.submissions.new(limit=post_limit) if x.created > date_limit and not
                           x.is_self and x.score < self.restrict_score_limit]
        else:
            submissions = [x for x in user.submissions.new(limit=post_limit) if x.created > date_limit and not
                           x.is_self]
        return submissions

    def get_submissions_subreddit(self, subreddit, date_limit, post_limit):
        """See get_submissions_user"""
        if self.subreddit_sort_method != 0:
            date_limit = 1
        if self.restrict_by_score and self.restrict_score_method == 0:
            submissions = [x for x in self.sub_sort(subreddit, post_limit) if not x.is_self and x.score >
                           self.restrict_score_limit and x.created > date_limit]
        elif self.restrict_by_score and self.restrict_score_method == 1:
            submissions = [x for x in self.sub_sort(subreddit, post_limit) if not x.is_self and x.score <
                           self.restrict_score_limit and x.created > date_limit]
        else:
            submissions = [x for x in self.sub_sort(subreddit, post_limit) if not x.is_self and x.created > date_limit]
        return submissions

    def sub_sort(self, sub, post_limit):  # new: 0, top: 1, hot: 2, rising: 3, controversial: 4
        sort = self.subreddit_sort_method
        if sort == 0:
            posts = sub.new(limit=post_limit)
        elif sort == 2:
            posts = sub.hot(limit=post_limit)
        elif sort == 3:
            posts = sub.rising(limit=post_limit)
        elif sort == 4:
            posts = sub.controversial(limit=post_limit)
        else:
            top_sort = self.subreddit_sort_top_method
            if top_sort == 0:
                posts = sub.top('hour', limit=post_limit)
            elif top_sort == 1:
                posts = sub.top('day', limit=post_limit)
            elif top_sort == 2:
                posts = sub.top('week', limit=post_limit)
            elif top_sort == 3:
                posts = sub.top('month', limit=post_limit)
            elif top_sort == 4:
                posts = sub.top('year', limit=post_limit)
            else:
                posts = sub.top('all', limit=post_limit)
        return posts

    def add_downloaded_user(self, user_tuple):
        if user_tuple[0] in self.downloaded_users:
            self.downloaded_users[user_tuple[0]].extend(user_tuple[1])
        else:
            self.downloaded_users[user_tuple[0]] = user_tuple[1]

    def send_downloaded_users(self):
        self.downloaded_users_signal.emit(self.downloaded_users)

    def stop_download(self):
        self.run = False
        self.stop.emit()
        self.queue.put('\nStopped\n')

    def send_unfinished_downloads(self):
        if not self.queued_posts.empty():
            for post in self.queued_posts.get():
                self.unfinished_downloads_signal.emit(post)

    def finish_downloads(self):
        self.queued_posts = self.unfinished_downloads_list
        self.download_number = len(self.queued_posts)
        self.status_bar_update.emit('Downloaded: 0  of  %s' % self.download_number)
        self.start_downloader()

    def skip_user_validation(self):
        for x in self.user_list:
            self.validated_objects.put(x)

    def update_progress_bar(self):
        self.update_progress_bar_signal.emit()


class Extractor(QObject):

    finished = pyqtSignal()
    update_progress_bar = pyqtSignal()
    send_user = pyqtSignal(tuple)

    def __init__(self, queue, valid_objects, post_queue, user_extract):
        """
        A class that is extracts downloadable links from container websites who's links have been posted to reddit

        :param queue: The main window queue used to update the GUI output box
        :param valid_objects: Users or subreddits that have been validated
        :param post_queue: The queue where downloadable links are passed to be downloaded by the downloader thread
        """
        super().__init__()
        self.queue = queue
        self.validated_objects = valid_objects
        self.post_queue = post_queue
        self.user_extract = user_extract
        self.run = True

    def extract(self):
        """Calls the extract processes for each user or subreddit"""
        while self.run:
            working_object = self.validated_objects.get()
            if working_object is not None:
                working_object.load_unfinished_downloads()
                working_object.extract_content()
                if len(working_object.failed_extracts) > 0:
                    for entry in working_object.failed_extracts:
                        self.queue.put(entry)
                if len(working_object.content) > 0:
                    self.queue.put('Count %s' % len(working_object.content))
                    if self.user_extract:
                        self.send_user.emit((working_object.name, [x.filename for x in working_object.content]))
                for post in working_object.content:
                    post.install_queue(self.queue)
                    self.post_queue.put(post)
                self.update_progress_bar.emit()
            else:
                self.run = False
        self.post_queue.put(None)
        self.finished.emit()

    def stop(self):
        self.run = False


class Downloader(QObject):

    finished = pyqtSignal()

    def __init__(self, queue, thread_limit):
        """
        Class that spawns the separate download threads.  This is a separate class so it can be moved to its own thread
        and run simultaneously with post extraction.

        :param queue: The download queue in which extracted content is placed
        """
        super().__init__()
        self.queue = queue
        self.run = True

        self.download_pool = QThreadPool()
        self.download_pool.setMaxThreadCount(thread_limit)

    def download(self):
        """Spawns the download pool threads"""
        while self.run:
            post = self.queue.get()
            if post is not None:
                self.download_pool.start(post)
            else:
                self.run = False
        self.download_pool.waitForDone()
        self.finished.emit()

    def stop(self):
        self.run = False
        self.download_pool.clear()
