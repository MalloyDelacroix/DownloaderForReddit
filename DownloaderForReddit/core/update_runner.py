import logging
from datetime import datetime
from queue import Queue
from threading import Thread, Event
from PyQt5.QtCore import QObject, pyqtSignal

from .submission_handler import SubmissionHandler
from DownloaderForReddit.core.download.downloader import Downloader
from .runner import verify_run
from ..database.models import DownloadSession, Post
from ..utils import injector, reddit_utils
from ..messaging.message import Message


class UpdateRunner(QObject):

    """
    Updates posts with information from reddit that may have been added after the date the post was extracted.
    """

    finished = pyqtSignal()

    def __init__(self, run_method, **kwargs):
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
        self.reddit_instance = reddit_utils.get_reddit_instance()
        self.run_method = run_method
        self.reddit_object_id_list = kwargs.get('reddit_object_id_list', None)
        self.post_id_list = kwargs.get('post_id_list', None)

        self.stop_run = Event()
        self.continue_run = True
        self.post_queue = Queue(maxsize=-1)
        self.download_thread = None
        self.downloader = None
        self.download_queue = Queue(maxsize=-1)
        self.download_session_id = None

    def run(self):
        self.logger.debug('Update runner starting')
        if self.run_method == 'UPDATE_SCORES':
            self.update_scores()
        elif self.run_method == 'UPDATE_COMMENTS':
            self.update_comments()
        self.logger.debug('Update runner finished')

    def create_download_session(self):
        with self.db.get_scoped_session() as session:
            count = session.query(DownloadSession.id).order_by(DownloadSession.id.desc()).first()[0] + 1
            download_session = DownloadSession(
                name=f'Update Session {count}',
                start_time=datetime.now(),
                download_thread_count=self.settings_manager.download_thread_count,
            )
            session.add(download_session)
            session.commit()
            self.download_session_id = download_session.id

    def finish_download_session(self):
        with self.db.get_scoped_update_session() as session:
            download_session = session.query(DownloadSession).get(self.download_session_id)
            download_session.end_time = datetime.now()

    def get_post_ids(self):
        """
        Extracts a list of post id's from the supplied reddit objects if the post_id list itself is not supplied.
        """
        if self.post_id_list is None:
            with self.db.get_scoped_session() as session:
                self.post_list = session.query(Post.id) \
                    .filter(Post.significant_reddit_object_id.in_(self.reddit_object_id_list)).all()

    @verify_run
    def update_scores(self):
        """Grabs the score for each post in the post_id_list and updates the post in the database with the new score."""
        self.get_post_ids()
        for post_id in self.post_id_list:
            self.extract_score(post_id)
        self.finished.emit()

    @verify_run
    def extract_score(self, post_id):
        with self.db.get_scoped_update_session() as session:
            try:
                post = session.query(Post).get(post_id)
                submission = self.reddit_instance.submission(id=post.reddit_id)
                old_score = post.score
                post.score = submission.score
                Message.send_info(f'{post.title} score updated\n'
                                  f'    Old score: {old_score}  |  New Score: {post.score}')
            except:
                self.logger.error('Failed to update post', extra={'post_id': post.id, 'post_title': post.title,
                                                                  'author': post.author.name,
                                                                  'subreddit': post.subreddit.name}, exc_info=True)
                Message.send_warning(f'Failed to update score for {post.title}')

    @verify_run
    def update_comments(self):
        """
        Queries the submission that the post is based on from reddit and iterates through the comments, extracting new
        ones as specified by the significant reddit objects comment settings.
        """
        self.create_download_session()
        self.start_downloader()
        self.get_post_ids()
        for post_id in self.post_id_list:
            self.extract_comments(post_id)
        self.download_queue.put(None)
        self.download_thread.join()
        self.finish_download_session()
        self.finished.emit()

    def start_downloader(self):
        self.downloader = Downloader(self.download_queue, self.download_session_id)
        self.download_thread = Thread(target=self.downloader.run)
        self.download_thread.start()

    @verify_run
    def extract_comments(self, post_id):
        with self.db.get_scoped_session() as session:
            post = session.query(Post).get(post_id)
            submission = self.reddit_instance.submission(id=post.reddit_id)
            submission_handler = SubmissionHandler(submission, post, self.download_session_id, session,
                                                   self.download_queue)
            submission_handler.extract_comments()

    def stop(self):
        self.stop_run.set()
