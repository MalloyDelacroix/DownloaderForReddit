import prawcore
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from queue import Queue
from threading import Thread
from datetime import datetime
from praw.models import Redditor

from ..Utils import Injector, RedditUtils, VideoMerger
from ..Core.SubmissionFilter import SubmissionFilter
from ..Core.ContentExtractor import ContentExtractor
from ..Core.Downloader import Downloader
from ..Database.Models import DownloadSession, User, Subreddit, Post, Content


class DownloadRunner(QObject):
    remove_invalid_object = pyqtSignal(object)
    remove_forbidden_object = pyqtSignal(object)
    finished = pyqtSignal()
    download_session_signal = pyqtSignal(int)  # emits the id of the DownloadSession created at the start of the run
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar_signal = pyqtSignal()
    update_download_potential = pyqtSignal(int)
    stop = pyqtSignal()

    def __init__(self, user_id_list=None, subreddit_id_list=None, perpetual=False):
        """
        Initializes the download runner with the settings needed to perform the download session.
        :param user_id_list: The list user id's queried from the database which is to be downloaded.  None indicates a
                             Subreddit download session.
        :param subreddit_id_list: The list subreddit id's queried from the database containing subreddits to be
                                  downloaded.  None indicates a User download.
        :param perpetual: Indicates whether the downloader should stop after it makes it through the entire list or if
                          it should continue to monitor for new posts.
        :type user_id_list: RedditObjectList
        :type subreddit_id_list: RedditObjectList
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
        self.download_type = 'USER' if user_id_list is not None else 'SUBREDDIT'
        self.validated_subreddits = []

        self.submission_queue = Queue()
        self.extractor = None
        self.extraction_thread = None
        self.download_queue = Queue()
        self.downloader = None
        self.download_thread = None

        self.user_id_list = user_id_list
        self.subreddit_id_list = subreddit_id_list
        self.perpetual = perpetual
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
        self.finished.emit()

    def create_download_session(self):
        with self.db.get_scoped_session() as session:
            download_session = DownloadSession(
                start_time=datetime.now(),
                extraction_thread_count=self.settings_manager.extraction_thread_count,
                download_thread_count=self.settings_manager.download_thread_count,
            )
            session.add(download_session)
            session.commit()
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
        if self.user_id_list is not None and self.subreddit_id_list is not None:
            self.filter_subreddits = True
            self.validate_subreddit_list()
        if self.user_id_list is not None:
            for user_id in self.user_id_list:
                self.get_user_submissions(user_id)
        else:
            for subreddit_id in self.subreddit_id_list:
                self.get_subreddit_submissions(subreddit_id)

    def validate_subreddit_list(self):
        with self.db.get_scoped_session() as session:
            for subreddit_id in self.subreddit_id_list:
                subreddit = session.query(Subreddit).get(subreddit_id)
                sub = self.validate_subreddit(subreddit)
                if sub is not None:
                    self.validated_subreddits.append(sub)
                else:
                    subreddit.set_inactive()

    def get_user_submissions(self, user_id):
        with self.db.get_scoped_session() as session:
            user = session.query(User).get(user_id)
            redditor = self.validate_user(user)

            if redditor is not None:
                submissions = self.get_submissions(redditor, user)
                date_limit = 0
                potential_downloads = 0
                for submission in submissions:
                    if submission.created > date_limit:
                        date_limit = submission.created
                    self.submission_queue.put((submission, user_id))
                    potential_downloads += 1
                user.set_date_limit(date_limit)  # date limit modified after submissions are extracted
                self.update_download_potential.emit(potential_downloads)
            else:
                user.set_inactive()

    def get_subreddit_submissions(self, subreddit_id):
        with self.db.get_scoped_session() as session:
            subreddit = session.query(Subreddit).get(subreddit_id)
            sub = self.validate_subreddit(subreddit)

            if sub is not None:
                submissions = self.get_submissions(sub, subreddit)
                date_limit = 0
                potential_downloads = 0
                for submission in submissions:
                    if submission.created > date_limit:
                        date_limit = submission.created
                    self.submission_queue.put((submission, subreddit_id))
                    potential_downloads += 1
                subreddit.set_date_limit(date_limit)
                self.update_download_potential.emit(potential_downloads)
            else:
                subreddit.set_inactive()

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
        sort_method = reddit_object.post_sort_method
        if sort_method.value <= 4:
            submission_method = self.get_raw_submission_method(praw_object, sort_method.name.lower())
            return submission_method(limit=reddit_object.post_limit)
        else:
            sort, sort_period = sort_method.name.split('_')
            submission_method = self.get_raw_submission_method(praw_object, sort.lower())
            return submission_method(sort_period, limit=reddit_object.post_limit)

    def get_raw_submission_method(self, praw_object, sort_type: str):
        """
        Creates and returns the method that should be used to retrieve the submissions for the praw_object.
        :param praw_object: The praw object for which submissions will be retrieved.
        :param sort_type: The sort method that should be used to retrieve these submissions.
        :return: A method that can be called to retrieve submissions from the supplied praw object which will be sorted
                 by the supplied sort method.
        """
        if type(praw_object) == Redditor:
            return getattr(praw_object.submissions, sort_type)
        else:
            return getattr(praw_object, sort_type)

    def finish_download(self):
        self.submission_queue.put(None)
        self.extraction_thread.join()
        self.download_thread.join()
        VideoMerger.merge_videos()
        with self.db.get_scoped_session() as session:
            dl_session = self.finish_download_session(session)
            self.finish_messages(dl_session, session)
        self.download_session_signal.emit(self.download_session_id)

    def finish_download_session(self, session):
        download_session = session.query(DownloadSession).get(self.download_session_id)
        download_session.end_time = datetime.now()
        session.commit()
        return download_session

    def finish_messages(self, dl_session, session):
        downloaded_post_count = session.query(Post.id).filter(Post.download_session == dl_session).count()
        downloaded_content_count = session.query(Content.id).filter(Content.download_session == dl_session).count()
        downloaded_object_count = \
            session.query(Post.significant_reddit_object_id).filter(Post.download_session == dl_session) \
            .distinct().count()
        self.logger.info('Download complete', extra={
            'download_time': dl_session.duration,
            'downloaded_reddit_object_count': downloaded_object_count,
            'extraction_count': downloaded_post_count,
            'download_count': downloaded_content_count,
        })
        message = f'\nFinished\nRun Time: {dl_session.duration}\n' \
                  f'Downloaded {self.download_type.lower()}s: {downloaded_object_count}\n' \
                  f'Extraction Count: {downloaded_post_count}\n' \
                  f'Download Count: {downloaded_content_count}'
        self.message_queue.put(message)

    def stop_download(self):
        self.continue_run = False
