import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Empty

from .runner import Runner, verify_run
from .submission_handler import SubmissionHandler
from .submittable_creator import SubmittableCreator
from ..database.models import Post
from ..utils import injector, reddit_utils


class ContentRunner(Runner):

    def __init__(self, submission_queue, download_queue, download_session_id, stop_run):
        super().__init__(stop_run)
        self.logger = logging.getLogger(__name__)
        self.submission_queue = submission_queue
        self.download_queue = download_queue
        self.download_session_id = download_session_id
        self.output_queue = injector.get_message_queue()
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()

        self.thread_count = self.settings_manager.extraction_thread_count
        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)
        self.futures = []
        self.hold = False
        self.submit_hold = False

    @property
    def running(self):
        if self.hold:
            return len(self.futures) > 0
        return True

    def run(self):
        self.logger.debug('Content extractor running')
        while self.continue_run:
            try:
                item = self.submission_queue.get(timeout=2)
                if item is not None:
                    if item == 'HOLD':
                        self.hold = True
                        self.submit_hold = True
                    elif item == 'RELEASE_HOLD':
                        self.hold = False
                        self.download_queue.put('RELEASE_HOLD')
                    else:
                        extraction_type, extraction_object, significant_id = item
                        if extraction_type == 'SUBMISSION':
                            future = self.executor.submit(self.handle_submission, submission=extraction_object,
                                                          significant_id=significant_id)
                        else:
                            future = self.executor.submit(self.finish_post, post_id=extraction_object)
                        future.add_done_callback(self.remove_future)
                        self.futures.append(future)
                else:
                    break
            except Empty:
                if self.submit_hold and not self.running:
                    self.download_queue.put('HOLD')
                    self.submit_hold = False
        self.executor.shutdown(wait=True)
        self.download_queue.put(None)
        self.logger.debug('Content extractor exiting')

    def remove_future(self, future):
        self.futures.remove(future)

    @verify_run
    def handle_submission(self, submission, significant_id):
        """
        Takes a reddit submission and creates a Post from its data.  Then calls the appropriate methods for the post.
        If comments are to be extracted from the submission, this is also handled here.
        :param submission: The reddit submission that is to be extracted.
        :param significant_id: The id of the reddit object for which the submissions was extracted from reddit.
        """
        with self.db.get_scoped_session() as session:
            post = SubmittableCreator.create_post(submission, significant_id, session, self.download_session_id)
            if post is not None:
                submission_handler = SubmissionHandler(submission, post, self.download_session_id, session,
                                                       self.download_queue, self.stop_run)
                submission_handler.extract_submission()
                if post.significant_reddit_object.run_comment_operations:
                    submission_handler.extract_comments()

    def finish_post(self, post_id):
        with self.db.get_scoped_session() as session:
            post = session.query(Post).get(post_id)
            self.handle_post(post)

    @verify_run
    def handle_post(self, post):
        """
        Calls the appropriate methods for the supplied post.
        :param post: The post that is to be extracted.
        """
        with self.db.get_scoped_session() as session:
            submission_handler = SubmissionHandler(None, post, self.download_session_id, session, self.download_queue,
                                                   self.stop_run)
            if not post.is_self:
                submission_handler.extract_submission_content()
            else:
                submission_handler.extract_self_post()
            if post.significant_reddit_object.run_comment_operations:
                submission = reddit_utils.get_reddit_instance().submission(post.reddit_id)
                submission_handler.submission = submission
                submission_handler.extract_comments()
