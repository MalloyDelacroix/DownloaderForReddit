import platform
import logging
from queue import Queue, Empty
from threading import Thread, Event
from datetime import datetime
import prawcore
from PyQt5.QtCore import QObject, pyqtSignal
from collections import namedtuple
from praw.models import Redditor
from sqlalchemy import or_

from DownloaderForReddit.core.download.downloader import Downloader
from .content_runner import ContentRunner
from .submission_filter import SubmissionFilter
from .runner import verify_run
from .errors import NON_DOWNLOADABLE
from ..database.models import DownloadSession, RedditObject, User, Subreddit, Post, Content
from ..utils import injector, reddit_utils, video_merger
from ..messaging.message import Message
from ..version import __version__


ExtractionSet = namedtuple('ExtractionSet', 'extraction_type extraction_object significant_id')
RunPair = namedtuple('RunPair', 'reddit_object_id praw_object')


class DownloadRunner(QObject):

    remove_invalid_object = pyqtSignal(int)
    remove_forbidden_object = pyqtSignal(int)
    finished = pyqtSignal()
    download_session_signal = pyqtSignal(int)  # emits the id of the DownloadSession created at the start of the run
    setup_progress_bar = pyqtSignal(int)
    update_progress_bar_signal = pyqtSignal()

    def __init__(self, user_id_list=None, subreddit_id_list=None, reddit_object_id_list=None, **kwargs):
        """
        Initializes the download runner with the settings needed to perform the download session.
        :param user_id_list: The list user id's queried from the database which is to be downloaded.  None indicates a
                             Subreddit download session.
        :param subreddit_id_list: The list subreddit id's queried from the database containing subreddits to be
                                  downloaded.  None indicates a User download.
        :type user_id_list: RedditObjectList
        :type subreddit_id_list: RedditObjectList
        """
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = injector.get_database_handler()
        self.settings_manager = injector.get_settings_manager()
        self.reddit_instance = reddit_utils.get_reddit_instance()
        self.submission_filter = SubmissionFilter()

        self.user_id_list = user_id_list
        self.subreddit_id_list = subreddit_id_list
        self.reddit_object_id_list = reddit_object_id_list
        self.run_unextracted = kwargs.get('run_unextracted', False)
        self.unextracted_id_list = kwargs.get('unextracted_id_list', None)
        self.run_undownloaded = kwargs.get('run_undownloaded', False)
        self.undownloaded_id_list = kwargs.get('undownloaded_id_list', None)
        self.run_new = kwargs.get('run_new', True)

        self.stop_run = Event()
        self.continue_run = True
        self.stopped = False
        self.filter_subreddits = False
        self.validated_subreddits = []

        self.submission_queue = Queue(maxsize=-1)
        self.extractor = None
        self.extraction_thread = None
        self.download_queue = Queue(maxsize=-1)
        self.downloader = None
        self.download_thread = None

        self.perpetual_download = self.settings_manager.perpetual_download
        self.perpetual_queue = Queue(maxsize=-1)
        self.failed_connection_attempts = 0
        self.download_session_id = None

        self.reddit_object_queue = Queue(maxsize=-1)

    def validate_user(self, user_obj):
        redditor = self.reddit_instance.redditor(user_obj.name)
        if self.validate_object(redditor, user_obj):
            Message.send_debug(f'{user_obj.name} is valid')
            return redditor
        else:
            return None

    def validate_subreddit(self, subreddit_obj):
        subreddit = self.reddit_instance.subreddit(subreddit_obj.name)
        if self.validate_object(subreddit, subreddit_obj):
            Message.send_debug(f'{subreddit_obj.name} is valid')
            return subreddit
        else:
            return None

    def validate_object(self, praw_object, reddit_object):
        try:
            praw_object.fullname
            return True
        except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, AttributeError):
            self.handle_invalid_reddit_object(reddit_object)
            reddit_object.set_inactive()
        except prawcore.exceptions.Forbidden:
            self.handle_forbidden_reddit_object(reddit_object)
            reddit_object.set_inactive()
        except prawcore.RequestException:
            self.handle_failed_connection()
        except:
            self.handle_unknown_error(reddit_object)
        return False

    def handle_invalid_reddit_object(self, reddit_object):
        self.logger.warning('Invalid reddit object detected', extra={'object_type': reddit_object.object_type,
                                                                     'reddit_object': reddit_object.name})
        Message.send_warning(f'Invalid {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_invalid_object.emit(reddit_object.id)

    def handle_forbidden_reddit_object(self, reddit_object):
        self.logger.warning('Forbidden reddit object detected', extra={'object_type': reddit_object.object_type,
                                                                       'reddit_object': reddit_object.name})
        Message.send_warning(f'Forbidden {reddit_object.object_type.lower()}: {reddit_object.name}')
        self.remove_forbidden_object.emit(reddit_object.id)

    def handle_failed_connection(self):
        if self.failed_connection_attempts >= 3:
            self.continue_run = False
            self.logger.error('Failed connection attempts exceeded.  Ending download session', exc_info=True)
            Message.send_critical('Failed connection attempts exceeded.  The download session has been canceled.  '
                                  'Please try the download again later.')
        else:
            self.logger.error('Failed to connect to reddit',
                              extra={'connection_attempts': self.failed_connection_attempts})
            Message.send_error(f'Failed to connect to reddit.  Connection attempts remaining: '
                               f'{3 - self.failed_connection_attempts}')
            self.failed_connection_attempts += 1

    def handle_unknown_error(self, reddit_object):
        self.logger.error('Failed to validate reddit object due to unknown error',
                          extra={'object_type': reddit_object.object_type, 'reddit_object': reddit_object.name},
                          exc_info=True)

    def run_unextracted_posts(self):
        self.logger.debug('Running unextracted posts')
        post_id_list = self.unextracted_id_list
        if post_id_list is None:
            with self.db.get_scoped_session() as session:
                post_id_list = session.query(Post.id)\
                    .filter(Post.extracted == False) \
                    .filter(Post.retry_attempts <= 3) \
                    .filter(or_(Post.extraction_error == None, Post.extraction_error.notin_(NON_DOWNLOADABLE)))
        self.logger.debug(f'{post_id_list.count()} unfinished posts to download')
        for post_id, in post_id_list.all():  # comma used to unpack result tuple
            extraction_set = ExtractionSet(extraction_type='POST', extraction_object=post_id, significant_id=None)
            self.submission_queue.put(extraction_set)
        self.logger.debug('Finished unextracted posts')

    def run_undownloaded_content(self):
        self.logger.debug('Running undownloaded content')
        content_id_list = self.undownloaded_id_list
        if content_id_list is None:
            with self.db.get_scoped_session() as session:
                content_id_list = session.query(Content)\
                    .filter(Content.downloaded == False) \
                    .filter(Content.retry_attempts <= 3) \
                    .filter(or_(Content.download_error == None, Content.download_error.notin_(NON_DOWNLOADABLE)))
        self.logger.debug(f'{content_id_list.count()} unfinished content items to download')
        for content in content_id_list.all():
            self.download_queue.put(content.id)
        self.logger.debug('Finished undownloaded content')

    def run(self):
        self.create_download_session()
        self.start_extractor()
        self.start_downloader()
        if self.run_unextracted:
            self.run_unextracted_posts()
        if self.run_undownloaded:
            self.run_undownloaded_content()
        if self.run_new:
            self.run_download()
        if self.perpetual_download:
            self.perpetuate_run()
        else:
            self.hold()

    def log_download_settings(self):
        self.logger.info('Download runner started.', extra={
            'dfr_version': __version__,
            'platform': platform.platform,
            'account_connected': reddit_utils.connection_is_authorized,
            'run_unextracted': self.run_unextracted,
            'run_undownloaded': self.run_undownloaded,
            'run_new': self.run_new,
            'perpetual_download': self.perpetual_download,
            'last_update': self.settings_manager.last_update,
            'extraction_thread_count': self.settings_manager.extraction_thread_count,
            'download_thread_count': self.settings_manager.download_thread_count,
            'multi_part_threshold': self.settings_manager.multi_part_threshold,
            'finish_incomplete_extractions': self.settings_manager.finish_incomplete_extractions_at_session_start,
            'finish_incomplete_downloads': self.settings_manager.finish_incomplete_downloads_at_session_start,
        })

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
        self.extractor = ContentRunner(self.submission_queue, self.download_queue, self.download_session_id,
                                       self.stop_run)
        self.extraction_thread = Thread(target=self.extractor.run)
        self.extraction_thread.start()

    def start_downloader(self):
        self.downloader = Downloader(self.download_queue, self.download_session_id, self.stop_run)
        self.download_thread = Thread(target=self.downloader.run)
        self.download_thread.start()

    def run_download(self):
        if self.reddit_object_id_list is not None:
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
        """
        Validates the list of subreddits to make sure they all exist so that the user list can be constrained to the
        list of verified subreddits.
        """
        with self.db.get_scoped_session() as session:
            for subreddit_id in self.subreddit_id_list:
                if self.continue_run:
                    subreddit = session.query(Subreddit).get(subreddit_id)
                    sub = self.validate_subreddit(subreddit)
                    if sub is not None:
                        self.validated_subreddits.append(sub)
                    else:
                        subreddit.set_inactive()
                else:
                    break

    @verify_run
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

    @verify_run
    def get_user_submissions(self, user_id, session=None):
        if session is None:
            with self.db.get_scoped_session() as session:
                return self.get_user_submissions(user_id, session=session)
        user = session.query(User).get(user_id)
        user.set_existing()
        redditor = self.validate_user(user)

        if redditor is not None:
            self.handle_submissions(user, redditor)

    @verify_run
    def get_subreddit_submissions(self, subreddit_id, session=None):
        if session is None:
            with self.db.get_scoped_session() as session:
                return self.get_subreddit_submissions(subreddit_id, session=session)
        subreddit = session.query(Subreddit).get(subreddit_id)
        subreddit.set_existing()
        sub = self.validate_subreddit(subreddit)

        if sub is not None:
            self.handle_submissions(subreddit, sub)

    def handle_submissions(self, reddit_object, praw_object):
        submissions = self.get_submissions(praw_object, reddit_object)
        date_limit = 0
        for submission in submissions:
            if submission.created > date_limit:
                date_limit = submission.created
            extraction_set = ExtractionSet(extraction_type='SUBMISSION', extraction_object=submission,
                                           significant_id=reddit_object.id)
            self.submission_queue.put(extraction_set)
        if date_limit > 0:
            reddit_object.set_date_limit(date_limit)  # date limit modified after submissions are extracted
        if self.perpetual_download:
            pair = RunPair(reddit_object_id=reddit_object.id, praw_object=praw_object)
            self.perpetual_queue.put(pair)

    @verify_run
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
            if (submission.pinned or submission.stickied) or passes_date_limit:
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

    def perpetuate_run(self):
        """
        Enters a perpetual loop that recycles reddit objects from the perpetual queue and checks for new posts.  After
        each object from the perpetual queue is checked, a check is also performed for new reddit objects that may have
        been added to the session after it began.
        """
        self.logger.debug('Entering perpetual run')
        while self.continue_run:
            self.run_next_perpetual_pair()
            self.check_added_object_queue(block=False)
        self.finish_download()

    def run_next_perpetual_pair(self):
        """
        Extracts a run_pair from the perpetual download queue and checks it for new submissions.
        """
        try:
            run_pair = self.perpetual_queue.get(timeout=1)
            if run_pair is not None:
                reddit_object_id, praw_object = run_pair
                with self.db.get_scoped_session() as session:
                    reddit_object = session.query(RedditObject).get(reddit_object_id)
                    self.handle_submissions(reddit_object, praw_object)
        except Empty:
            pass

    def hold(self):
        """
        Holds the download runner while the content extractor and downloader finish their work loads.  During this time,
        reddit objects that were not initially in the download list can be added to the download queue.
        """
        self.logger.debug('DownloadRunner holding')
        self.submission_queue.put('HOLD')
        while self.continue_run and (self.extractor.running or self.downloader.running):
            self.check_added_object_queue()
        self.finish_download()

    def check_added_object_queue(self, block=True):
        """
        Checks the added reddit object queue to see if a new reddit object has been added to the download session after
        it began running.
        :param block: Indicates whether the reddit object queue check should block or not.  The default is True, which
                      should be used for holding.  False would be used if a quick check is to happen, but monitoring
                      the queue is not the main activity.
        """
        try:
            reddit_object_id = self.reddit_object_queue.get(timeout=1, block=block)
            if reddit_object_id is not None:
                self.submission_queue.put('RELEASE_HOLD')
                self.get_reddit_object_submissions(reddit_object_id)
                self.submission_queue.put('HOLD')  # reapply holds after new submissions added to queue
        except Empty:
            pass

    def finish_download(self):
        """
        Wraps up the download session by shutting down the extractor and downloader, adding the finishing information
        to the download session model, saving it to the database and generally any cleanign up that needs to happen.
        """
        self.logger.debug('DownloadRunner finished')
        self.submission_queue.put(None)
        try:
            self.extraction_thread.join()
        except AttributeError:
            pass
        try:
            self.download_thread.join()
        except AttributeError:
            pass
        video_merger.merge_videos()
        with self.db.get_scoped_session() as session:
            dl_session = self.finish_download_session(session)
            self.finish_messages(dl_session)
        self.download_session_signal.emit(self.download_session_id)
        self.finished.emit()

    def finish_download_session(self, session):
        """
        Adds the finishing information to the current download session and commits it to the database.
        :param session: The sqlalchemy session that is active for use in committing the download session to storage.
        :return: The finished download session with all it's information.
        """
        download_session = session.query(DownloadSession).get(self.download_session_id)
        download_session.end_time = datetime.now()
        session.commit()
        return download_session

    def finish_messages(self, dl_session):
        """
        Constructs and displays a finish message to the user and a log message.
        :param dl_session: The active download session for this run.
        """
        significant_user_count = dl_session.get_downloaded_user_count()
        total_user_count = dl_session.get_downloaded_user_count(significant=False)
        significant_subreddit_count = dl_session.get_downloaded_subreddit_count()
        total_subreddit_count = dl_session.get_downloaded_subreddit_count(significant=False)
        extracted_post_count = dl_session.get_extracted_post_count()
        extracted_comment_count = dl_session.get_comment_count()
        downloaded_content_count = dl_session.get_downloaded_content_count()
        extra = {
            'download_time': dl_session.duration_display,
            'significant_user_count': significant_user_count,
            'significant_subreddit_count': significant_subreddit_count,
            'total_user_count': total_user_count,
            'total_subreddit_count': total_subreddit_count,
            'post_extraction_count': extracted_post_count,
            'comment_extraction_count': extracted_comment_count,
            'download_count': downloaded_content_count,
        }
        message = f'Finished\nRun Time: {dl_session.duration_display}\n' \
                  f'Download Count: {downloaded_content_count}\n' \
                  f'Downloaded Users: {significant_user_count}\n' \
                  f'Downloaded Subreddits: {significant_subreddit_count}\n' \
                  f'Post Count: {extracted_post_count}\n' \
                  f'Comment Count: {extracted_comment_count}\n'
        if self.stopped:
            extra.update(download_stopped=True)
            message = f'\nDownload stopped{message}'
        self.logger.info('Download complete', extra=extra)
        Message.send_info('\n' + message)
        Message.send_status_tray(message)

    def stop_download(self, hard_stop=False):
        self.stopped = True
        self.continue_run = False
        self.stop_run.set()
        self.downloader.hard_stop = hard_stop
        Message.send_warning('\nStopped\n')
