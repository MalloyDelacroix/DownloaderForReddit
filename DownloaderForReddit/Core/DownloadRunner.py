import prawcore
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from queue import Queue, Empty
from threading import Thread
from datetime import datetime
from praw.models import Redditor

from ..Utils import Injector, RedditUtils, VideoMerger
from ..Core.SubmissionFilter import SubmissionFilter
from ..Core.ContentExtractor import ContentExtractor
from ..Core.Downloader import Downloader
from ..Database.Models import DownloadSession, RedditObject, User, Subreddit, Post, Content, Comment
from ..Messaging.Message import Message


class DownloadRunner(QObject):

    remove_invalid_object = pyqtSignal(object)
    remove_forbidden_object = pyqtSignal(object)
    finished = pyqtSignal()
    download_session_signal = pyqtSignal(int)  # emits the id of the DownloadSession created at the start of the run
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar_signal = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self, user_id_list=None, subreddit_id_list=None, reddit_object_id_list=None, perpetual=False):
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
        self.db = Injector.get_database_handler()
        self.settings_manager = Injector.get_settings_manager()
        self.reddit_instance = RedditUtils.get_reddit_instance()
        self.submission_filter = SubmissionFilter()
        self.continue_run = True
        self.filter_subreddits = False
        self.download_type = 'USER' if user_id_list is not None else 'SUBREDDIT'  # TODO: set for ro download
        self.validated_subreddits = []

        self.submission_queue = Queue(maxsize=-1)
        self.extractor = None
        self.extraction_thread = None
        self.download_queue = Queue(maxsize=-1)
        self.downloader = None
        self.download_thread = None

        self.user_id_list = user_id_list
        self.subreddit_id_list = subreddit_id_list
        self.reddit_object_id_list = reddit_object_id_list
        self.perpetual = perpetual
        self.failed_connection_attempts = 0
        self.download_session_id = None

        self.reddit_object_queue = Queue(maxsize=-1)

    def validate_user(self, user_obj):
        redditor = None
        try:
            redditor = self.reddit_instance.redditor(user_obj.name)
            redditor.fullname  # validity check
            Message.send_text(f'{user_obj.name} is valid')
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
            Message.send_text(f'{subreddit_obj.name} is valid')
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
        Message.send_text(f'Invalid {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_invalid_object.emit(reddit_object)

    def handle_forbidden_reddit_object(self, reddit_object):
        self.logger.warning('Forbidden reddit object detected', extra={'object_type': reddit_object.object_type,
                                                                       'reddit_object': reddit_object.name})
        Message.send_text(f'Forbidden {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_invalid_object.emit(reddit_object)

    def handle_failed_connection(self):
        if self.failed_connection_attempts >= 3:
            self.continue_run = False
            self.logger.error('Failed connection attempts exceeded.  Shutting down run', exc_info=True)
            Message.send_text('Failed connection attempts exceeded.  The downloader has been shut down.  Please '
                                   'try the download again later.')
        else:
            self.logger.error('Failed to connect to reddit',
                              extra={'connection_attempts': self.failed_connection_attempts})
            Message.send_text(f'Failed to connect to reddit.  Connection attempts remaining: '
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
        self.hold()

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
        if self.reddit_object_id_list:
            for ro_id in self.reddit_object_id_list:
                self.get_reddit_object_submissions(ro_id)
        else:
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

    def get_reddit_object_submissions(self, reddit_object_id):
        """
        Takes a RedditObject id and then calls the appropriate method to get submissions for the object depending on
        what type of reddit object it is (user or subreddit)
        :param reddit_object_id: The id of the reddit object to be downloaded.
        """
        with self.db.get_scoped_session() as session:
            object_type = session.query(RedditObject.object_type).filter(RedditObject.id == reddit_object_id).first()
            if object_type[0] == 'USER':
                self.get_user_submissions(reddit_object_id, session=session)
            else:
                self.get_subreddit_submissions(reddit_object_id, session=session)

    def get_user_submissions(self, user_id, session=None):
        if session is None:
            with self.db.get_scoped_session() as session:
                self.get_user_submissions(user_id, session=session)
        user = session.query(User).get(user_id)
        redditor = self.validate_user(user)

        if redditor is not None:
            submissions = self.get_submissions(redditor, user)
            date_limit = 0
            for submission in submissions:
                if submission.created > date_limit:
                    date_limit = submission.created
                self.submission_queue.put((submission, user_id))
            user.set_date_limit(date_limit)  # date limit modified after submissions are extracted
        else:
            user.set_inactive()

    def get_subreddit_submissions(self, subreddit_id, session=None):
        if session is None:
            with self.db.get_scoped_session() as session:
                self.get_subreddit_submissions(subreddit_id, session=session)
        subreddit = session.query(Subreddit).get(subreddit_id)
        sub = self.validate_subreddit(subreddit)

        if sub is not None:
            submissions = self.get_submissions(sub, subreddit)
            date_limit = 0
            for submission in submissions:
                if submission.created > date_limit:
                    date_limit = submission.created
                self.submission_queue.put((submission, subreddit_id))
            subreddit.set_date_limit(date_limit)
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
            sort, sort_period = sort_method.name.lower().split('_')
            submission_method = self.get_raw_submission_method(praw_object, sort)
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

    def hold(self):
        self.logger.debug('DownloadRunner holding')
        self.submission_queue.put('HOLD')
        while self.extractor.running or self.downloader.running:
            try:
                reddit_object_id = self.reddit_object_queue.get(timeout=1)
                if reddit_object_id is not None:
                    self.submission_queue.put('RELEASE_HOLD')
                    self.get_reddit_object_submissions(reddit_object_id)
                    self.submission_queue.put('HOLD')  # reapply holds after new submissions added to queue
            except Empty:
                pass
        self.finish_download()

    def finish_download(self):
        self.logger.debug('DownloadRunner finished')
        self.submission_queue.put(None)
        self.extraction_thread.join()
        self.download_thread.join()
        VideoMerger.merge_videos()
        with self.db.get_scoped_session() as session:
            dl_session = self.finish_download_session(session)
            self.finish_messages(dl_session, session)
        self.download_session_signal.emit(self.download_session_id)
        self.finished.emit()

    def finish_download_session(self, session):
        download_session = session.query(DownloadSession).get(self.download_session_id)
        download_session.end_time = datetime.now()
        session.commit()
        return download_session

    def finish_messages(self, dl_session, session):
        extracted_post_count = session.query(Post.id).filter(Post.download_session_id == dl_session.id).count()
        extracted_comment_count = \
            session.query(Comment.id).filter(Comment.download_session_id == dl_session.id).count()
        downloaded_content_count = \
            session.query(Content.id).filter(Content.download_session_id == dl_session.id).count()
        downloaded_object_count = \
            session.query(Post.significant_reddit_object_id).filter(Post.download_session == dl_session) \
            .distinct().count()
        self.logger.info('Download complete', extra={
            'download_time': dl_session.duration,
            'downloaded_reddit_object_count': downloaded_object_count,
            'post_extraction_count': extracted_post_count,
            'comment_extraction_count': extracted_comment_count,
            'download_count': downloaded_content_count,
        })
        message = f'\nFinished\nRun Time: {dl_session.duration}\n' \
                  f'Downloaded {self.download_type.lower()}s: {downloaded_object_count}\n' \
                  f'Post Count: {extracted_post_count}\n' \
                  f'Comment Count: {extracted_comment_count}\n' \
                  f'Download Count: {downloaded_content_count}'
        Message.send_text(message)

    def stop_download(self):
        self.continue_run = False
