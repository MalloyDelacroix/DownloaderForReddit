import prawcore
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
from time import time
import logging
from queue import Queue

from ..Database.Models import User, Subreddit, Post
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
        """
        Initializes the download runner with the settings needed to perform the download session.
        :param user_list: The list object queried from the database which is to be downloaded.  None indicates a
                          Subreddit download session.
        :param subreddit_list: The list object queried from the database containing subreddits to be downloaded.  None
                               indicates a User download.
        :param perpetual: Indicates whether the downloader should stop after it makes it through the entire list or if
                          it should continue to monitor for new posts.
        :type user_list: RedditObjectList
        :type subreddit_list: RedditObjectList
        :type perpetual: bool
        """
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.message_queue = Injector.get_queue()
        self.db = Injector.get_database_handler()
        self.settings_manager = Injector.get_settings_manager()
        self.reddit_instance = RedditUtils.get_reddit_instance()
        self.submission_filter = SubmissionFilter()
        self.run = True
        self.filter_subreddits = False
        self.validated_subreddits = []

        self.extraction_queue = Queue()
        self.download_queue = Queue()

        self.user_list = user_list
        self.subreddit_list = subreddit_list
        self.perpetual = perpetual
        self.post_queue = Queue()
        self.failed_connection_attempts = 0

    def validate_user(self, user_obj):
        redditor = None
        try:
            redditor = self.reddit_instance.redditor(user_obj.name)
            redditor.fullname  # validity check
            self.message_queue.put(f'{user_obj.name} is valid')
            return redditor
        except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
            self.handle_invalid_reddit_object(user_obj)
        except prawcore.exceptions.Forbidden:
            self.handle_forbidden_reddit_object(user_obj)
        except prawcore.RequestException:
            self.handle_failed_connection()
        except:
            self.handle_unknown_error(user_obj)
        finally:
            return redditor

    def validate_subreddit(self, subreddit_obj):
        try:
            subreddit = self.reddit_instance.subreddit(subreddit_obj.name)
            subreddit.fullname  # validity check
            self.message_queue.put(f'{subreddit_obj.name} is valid')
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
        self.logger.warning('Invalid reddit object detected', extra={'object_type': reddit_object.object_type,
                                                                     'reddit_object': reddit_object.name})
        self.message_queue.put(f'Invalid {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_invalid_object.emit(reddit_object)

    def handle_forbidden_reddit_object(self, reddit_object):
        self.logger.warning('Forbidden reddit object detected', extra={'object_type': reddit_object.object_type,
                                                                       'reddit_object': reddit_object.name})
        self.message_queue.put(f'Forbidden {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_invalid_object.emit(reddit_object)

    def handle_failed_connection(self):
        if self.failed_connection_attempts >= 3:
            self.run = False
            self.logger.error('Failed connection attempts exceeded.  Shutting down run', exc_info=True)
            self.message_queue.put('Failed connection attempts exceeded.  The downloader has been shut down.  Please '
                                   'try the download again later.')
        else:
            self.logger.error('Failed to connect to reddit',
                              extra={'connection_attempts': self.failed_connection_attempts})
            self.message_queue.put(f'Failed to connect to reddit.  Connection attempts remaining: '
                                   f'{3 - self.failed_connection_attempts}')
            self.failed_connection_attempts += 1

    def handle_unknown_error(self, reddit_object):
        self.logger.error('Failed to validate reddit object due to unknown error',
                          extra={'object_type': reddit_object.object_type, 'reddit_object': reddit_object.name},
                          exc_info=True)

    def run_download(self):
        if self.user_list is not None and self.subreddit_list is not None:
            self.filter_subreddits = True
            self.validate_subreddit_list()
        if self.user_list is not None:
            for user in self.user_list:
                self.get_user_submissions(user)
        else:
            for subreddit in self.subreddit_list:
                self.get_subreddit_submissions(subreddit)

    def validate_subreddit_list(self):
        for subreddit in self.subreddit_list:
            sub = self.validate_subreddit(subreddit)
            if sub is not None:
                self.validated_subreddits.append(sub)

    def get_user_submissions(self, user):
        redditor = self.validate_user(user)
        if redditor is not None:
            submissions = self.get_submissions(redditor, user)
            for submission in submissions:
                post = self.create_post(submission)
                self.extraction_queue.put(post)

    def get_subreddit_submissions(self, subreddit):
        sub = self.validate_subreddit(subreddit)
        if sub is not None:
            submissions = self.get_submissions(sub, subreddit)
            for submission in submissions:
                post = self.create_post(submission)
                self.extraction_queue.put(post)

    def get_submissions(self, praw_object, reddit_object):
        submissions = []
        for submission in self.get_raw_submissions(praw_object, reddit_object):
            passes_date_limit = self.submission_filter.date_filter(submission, reddit_object)
            # stickied posts are taken first when getting submissions by new, even when they are not the newest
            # submissions.  So the first filter pass allows stickied posts through so they do not trip the date filter
            # before more recent posts are allowed through
            if submission.stickied or passes_date_limit:
                if passes_date_limit:
                    if (not self.filter_subreddits or submission.subreddit.display_name in self.validated_subreddits) \
                            and self.submission_filter.filter_submission(submission, reddit_object):
                        submissions.append(submission)
            else:
                break
        return submissions

    def get_raw_submissions(self, praw_object, reddit_object):
        if reddit_object.object_type == 'USER':
            posts = praw_object.submissions.new(limit=reddit_object.post_limit)
        else:
            sort = reddit_object.post_sort_method()
            if sort[0] == 'NEW':
                posts = praw_object.new(limit=reddit_object.post_limit)
            elif sort[0] == 'HOT':
                posts = praw_object.hot(limit=reddit_object.post_limit)
            elif sort[0] == 'RISING':
                posts = praw_object.rising(limit=reddit_object.post_limit)
            elif sort[0] == 'CONTROVERSIAL':
                posts = praw_object.controversial(limit=reddit_object.post_limit)
            else:
                posts = praw_object.top(sort[1].lower(), limit=reddit_object.post_limit)
        return posts

    def create_post(self, submission):
        author = self.db.get_or_create(User, name=submission.author.name)[0]
        subreddit = self.db.get_or_create(Subreddit, name=submission.subreddit.display_name)[0]
        post = Post(
            title=submission.title,
            date_posted=datetime.fromtimestamp(submission.created),
            domain=submission.domain,
            score=submission.score,
            nsfw=submission.over_18,
            reddit_id=submission.id,
            extraction_date=datetime.now(),
            url=submission.url,
            author=author,
            subreddit=subreddit
        )
        self.db.add(post)
        return post


class ExtractionRunner(QObject):

    pass


class Downloader(QObject):

    pass
