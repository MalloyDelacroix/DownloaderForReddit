import prawcore
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from queue import Queue
from threading import Thread
from datetime import datetime

from ..Utils import Injector, RedditUtils, VideoMerger
from ..Core.SubmissionFilter import SubmissionFilter
from ..Core.ContentExtractor import ContentExtractor
from ..Core.Downloader import Downloader
from ..Database.Models import DownloadSession


class DownloadRunner(QObject):

    remove_invalid_object = pyqtSignal(object)
    remove_forbidden_object = pyqtSignal(object)
    finished = pyqtSignal()
    download_session_signal = pyqtSignal(int)  # emits the id of the DownloadSession created at the start of the run
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
        self.message_queue = Injector.get_output_queue()
        self.db = Injector.get_database_handler()
        self.settings_manager = Injector.get_settings_manager()
        self.reddit_instance = RedditUtils.get_reddit_instance()
        self.submission_filter = SubmissionFilter()
        self.continue_run = True
        self.filter_subreddits = False
        self.download_type = 'USER' if user_list is not None else 'SUBREDDIT'
        self.validated_subreddits = []

        self.extraction_queue = Queue()
        self.extractor = None
        self.extraction_thread = None
        self.download_queue = Queue()
        self.downloader = None
        self.download_thread = None

        self.user_list = user_list
        self.subreddit_list = subreddit_list
        self.perpetual = perpetual
        self.submission_queue = Queue()
        self.failed_connection_attempts = 0
        self.download_session_id = None

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
            self.continue_run = False
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

    def run(self):
        self.create_download_session()
        self.start_extractor()
        self.start_downloader()
        self.run_download()
        self.finish_download()

    def create_download_session(self):
        download_session = DownloadSession(
            start_time=datetime.now(),
            extraction_thread_count=self.settings_manager.extraction_thread_count,
            download_thread_count=self.settings_manager.download_thread_count,
        )
        self.db.add(download_session)
        self.download_session_id = download_session.id

    def start_extractor(self):
        self.extractor = ContentExtractor(self.submission_queue, self.download_queue, self.download_session_id)
        self.extraction_thread = Thread(target=self.extractor.run)
        self.extraction_thread.start()

    def start_downloader(self):
        self.downloader = Downloader(self.download_queue, self.download_session_id)
        self.download_thread = Thread(target=self.downloader.run)
        self.download_thread.start()

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
            self.downloaded_object_count += 1
            submissions = self.get_submissions(redditor, user)
            date_limit = 0
            for submission in submissions:
                if submission.created > date_limit:
                    date_limit = submission.created
                self.extraction_queue.put(submission)
            user.set_date_limit(date_limit)  # date limit modified after submissions are extracted

    def get_subreddit_submissions(self, subreddit):
        sub = self.validate_subreddit(subreddit)
        if sub is not None:
            self.downloaded_object_count += 1
            submissions = self.get_submissions(sub, subreddit)
            for submission in submissions:
                subreddit.set_date_limit(submission.created)  # date limit modified after submissions are extracted
                self.extraction_queue.put(submission)

    def get_submissions(self, praw_object, reddit_object):
        """
        Extracts submissions from the supplied praw object's submission generator.  The submissions are passed through
        the SubmissionFilter before being added for extraction.
        :param praw_object: The praw object from which submissions are extracted.
        :param reddit_object: The reddit object which the praw object is based on.
        :return: A list of submissions extracted from reddit.  May be an empty list if no passing submissions are found.
        """
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
        if len(submissions) > 1:
            self.add_reddit_object_to_download_session(reddit_object)
        return submissions

    def get_raw_submissions(self, praw_object, reddit_object):
        """
        Returns a praw submission generator for the supplied praw object sorted and limited by the settings of the
        supplied reddit object.
        :param praw_object: The praw object (Redditor or Subreddit) from which a submission generator is to be returned.
        :param reddit_object: The reddit object matching the praw object which contains the settings to be used to sort
                              and limit the submission generator.
        :return: A submission generator for the supplied praw object.
        """
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

    def add_reddit_object_to_download_session(self, reddit_object):
        with self.db.get_scoped_session() as session:
            download_session = session.query(DownloadSession)\
                .filter(DownloadSession.id == self.download_session_id).first()
            download_session.reddit_objects.append(reddit_object)
            session.commit()

    def finish_download(self):
        self.submission_queue.put(None)
        self.extraction_thread.join()
        self.download_thread.join()
        VideoMerger.merge_videos()
        self.finish_download_session()
        self.finish_messages()
        self.download_session_signal.emit(self.download_session_id)

    def finish_download_session(self):
        with self.db.get_scoped_session() as session:
            download_session = session.query(DownloadSession)\
                .filter(DownloadSession.id == self.download_session_id).first()
            download_session.end_time = datetime.now()
            session.commit()

    def finish_messages(self):
        time_string = self.download_session.duration
        self.logger.info('Download complete', extra={
            'download_time': time_string,
            'downloaded_reddit_objects': self.downloaded_object_count,
            'extraction_count': self.extractor.content_count,
            'download_count': self.downloader.download_count,
        })
        message = f'\nFinished\nRun Time: {time_string}\n' \
                  f'Downloaded {self.download_type.lower()}s: {self.downloaded_object_count}\n' \
                  f'Extraction Count: {self.extractor.content_count}\n' \
                  f'Download Count: {self.downloader.download_count}'
        self.message_queue.put(message)
