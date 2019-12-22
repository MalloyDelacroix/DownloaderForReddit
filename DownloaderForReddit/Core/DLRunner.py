import prawcore
from PyQt5.QtCore import QObject, pyqtSignal
from time import time
import logging
from queue import Queue

from ..Database.Models import User, Subreddit
from ..Utils import Injector, RedditUtils, VideoMerger
from ..Core.SubmissionFilter import SubmissionFilter
from ..Core import Const
from ..Extractors.Extractor import Extractor


class DownloadRunner(QObject):

    remove_invalid_object = pyqtSignal(object)
    remove_forbidden_object = pyqtSignal(object)
    finished = pyqtSignal()
    downloaded_objects_signal = pyqtSignal(dict)
    failed_download_signal = pyqtSignal(object)
    status_bar_update = pyqtSignal(str)
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar_signal = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self, user_list=None, subreddit_list=None, perpetual=False):
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.queue = Injector.get_queue()
        self.db = Injector.get_database_handler()
        self.settings_manager = Injector.get_settings_manager()
        self.reddit_instance = RedditUtils.get_reddit_instance()
        self.submission_filter = SubmissionFilter()
        self.run = True

        self.user_list = user_list
        self.subreddit_list = subreddit_list
        self.perpetual = perpetual
        self.post_queue = Queue()

    def validate_user(self, user_obj):
        try:
            redditor = self.reddit_instance.redditor(user_obj.name)
            redditor.fullname  # validity check
            self.queue.put(f'{user_obj.name} is valid')
            return redditor
        except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
            self.handle_invalid_reddit_object(user_obj)
        except prawcore.exceptions.Forbidden:
            self.handle_forbidden_reddit_object(user_obj)
        except prawcore.RequestException:
            self.handle_failed_connection()
        except:
            self.handle_unknown_error(user_obj)

    def validate_subreddit(self, subreddit_obj):
        try:
            subreddit = self.reddit_instance.subreddit(subreddit_obj.name)
            subreddit.fullname  # validity check
            self.queue.put(f'{subreddit_obj.name} is valid')
            return subreddit
        except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
            self.handle_invalid_reddit_object(subreddit_obj)
        except prawcore.exceptions.Forbidden:
            self.handle_forbidden_reddit_object(subreddit_obj)
        except prawcore.RequestException:
            self.handle_failed_connection()
        except:
            self.handle_unknown_error(subreddit_obj)

    def handle_invalid_reddit_object(self, reddit_object):
        pass

    def handle_forbidden_reddit_object(self, reddit_object):
        pass

    def handle_failed_connection(self):
        pass

    def handle_unknown_error(self, reddit_object):
        pass

    def run(self):
        pass

    def check_for_posts(self):
        if self.user_list is not None and self.subreddit_list is not None:
            self.get_user_posts_from_subreddits()
        elif self.user_list is not None:
            self.get_user_posts()
        else:
            self.get_subreddit_posts()

    def get_user_posts(self):
        for user in self.user_list:
            if user.new:
                self.get_new_user_posts(user)
            else:
                self.get_existing_user_posts(user)

    def get_new_user_posts(self, user):
        redditor = self.validate_user(user)
        if redditor is not None:
            posts = self.get_date_filtered_user_submission(redditor, user, None)
            for post in self.filter_submissions(user, posts):
                self.post_queue.put({'post': post, 'reddit_object': user})

    def get_existing_user_posts(self, user):
        redditor = self.validate_user(user)
        if redditor is not None:
            posts = self.get_new_submissions_for_user(redditor, user)
            for post in self.filter_submissions(user, posts):
                self.post_queue.put({'post': post, 'reddit_object': user})

    def get_new_submissions_for_user(self, redditor, user):
        pass

    def get_subreddit_posts(self):
        for sub in self.subreddit_list:
            if sub.new:
                self.get_new_subreddit_posts(sub)
            else:
                self.get_existing_subreddit_posts(sub)

    def get_new_subreddit_posts(self, subreddit):
        pass

    def get_existing_subreddit_posts(self, subreddit):
        pass

    def get_user_posts_from_subreddits(self):
        pass

    def get_new_user_posts_in_subreddits(self, user):
        pass

    def get_existing_user_posts_in_subreddits(self, user):
        pass

    def get_date_filtered_user_submission(self, redditor, user, limit):
        pass

    def filter_user_submissions_by_date(self, submissions, user):
        pass

    def get_raw_user_submissions(self, redditor, limit):
        pass

    def get_date_filtered_subreddit_submissions(self, sub, subreddit, limit):
        pass

    def get_filtered_subreddit_submissions(self, submissions, subreddit):
        pass

    def get_raw_subreddit_submissions(self, sub, subreddit, limit):
        pass

    def filter_submissions(self, reddit_object, submission_list):
        return [self.make_post_object(submission) for submission in submission_list if
                self.submission_filter.filter_submission(submission, reddit_object)]

    def make_post_object(self, submission):
        pass
