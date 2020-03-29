from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from praw.models import Submission
from queue import Empty

from ..Extractors.BaseExtractor import BaseExtractor
from ..Extractors.DirectExtractor import DirectExtractor
from ..Database.Models import User, Subreddit, Post
from ..Utils import Injector
from ..Core import Const


class ContentExtractor:

    def __init__(self, submission_queue, download_queue, download_session_id):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.submission_queue = submission_queue
        self.download_queue = download_queue
        self.download_session_id = download_session_id
        self.output_queue = Injector.get_message_queue()
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()

        self.thread_count = self.settings_manager.extraction_thread_count
        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)
        self.hold = False
        self.submit_hold = False
        self.continue_run = True
        self.content_count = 0

    @property
    def running(self):
        if self.hold:
            return not self.executor._work_queue.empty()
        return True

    def run(self):
        self.logger.debug('Content extractor running')
        while self.continue_run:
            item = self.submission_queue.get()
            if item is not None:
                if item == 'HOLD':
                    self.hold = True
                    self.download_queue.put('HOLD')
                elif item == 'RELEASE_HOLD':
                    self.hold = False
                    self.download_queue.put('RELEASE_HOLD')
                else:
                    submission = item[0]
                    siginificant_id = item[1]
                    self.handle_submission(submission, siginificant_id)
            else:
                self.continue_run = False
        self.executor.shutdown(wait=True)
        self.download_queue.put(None)
        self.logger.debug('Content extractor exiting')

    # def run(self):
    #     self.logger.debug('Content extractor running')
    #     while self.continue_run:
    #         try:
    #             item = self.submission_queue.get(timeout=2)
    #             if item is not None:
    #                 if item == 'HOLD':
    #                     self.hold = True
    #                     self.submit_hold = True
    #                     # self.download_queue.put('HOLD')
    #                 elif item == 'RELEASE_HOLD':
    #                     self.hold = False
    #                     self.download_queue.put('RELEASE_HOLD')
    #                 else:
    #                     submission = item[0]
    #                     significant_id = item[1]
    #                     self.executor.submit(self.handle_submission, submission=submission, significant_id=significant_id)
    #             else:
    #                 self.continue_run = False
    #         except Empty:
    #             if self.submit_hold and not self.running:
    #                 self.download_queue.put('HOLD')
    #                 self.submit_hold = False
    #     self.executor.shutdown(wait=True)
    #     self.download_queue.put(None)
    #     self.logger.debug('Content extractor exiting')

    def handle_submission(self, submission, significant_id):
        with self.db.get_scoped_session() as session:
            post = self.create_post(submission, significant_id, session)
            if post is not None:
                self.extract(post)

    def create_post(self, submission: Submission, significant_id: int, session) -> Optional[Post]:
        post = None
        if self.check_duplicate_post_url(submission.url, session):
            author = self.db.get_or_create(User, name=submission.author.name, session=session)[0]
            subreddit = self.db.get_or_create(Subreddit, name=submission.subreddit.display_name, session=session)[0]
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
                subreddit=subreddit,
                download_session_id=self.download_session_id,
                significant_reddit_object_id=significant_id
            )
            session.add(post)
            session.commit()
        return post

    def check_duplicate_post_url(self, url, session):
        return session.query(Post.id).filter(Post.url == url).scalar() is None

    def extract(self, post: Post):
        try:
            extractor = self.assign_extractor(post)(post)
            if extractor is not None:
                extractor.extract_content()
                if not extractor.failed_extraction:
                    post.set_extracted()
                for content in extractor.extracted_content:
                    self.content_count += 1
                    self.download_queue.put(content.id)
            else:
                self.handle_unsupported_domain(post)
        except ConnectionError:
            self.handle_connection_error(post)
        except:
            self.handle_unknown_error(post)

    def assign_extractor(self, post):
        for extractor in BaseExtractor.__subclasses__():
            key = extractor.get_url_key()
            if key is not None and any(x in post.url.lower() for x in key):
                return extractor
        if post.url.lower().endswith(Const.ALL_EXT):
            return DirectExtractor
        return None

    def handle_unsupported_domain(self, post):
        message = 'Unsupported domain'
        self.log_error(post, message, domain=post.domain)
        post.set_extraction_failed(message)
        self.output_error(post, message)

    def handle_connection_error(self, post):
        message = 'Failed to establish a connection to the server'
        self.log_error(post, message)
        post.set_extraction_failed(message)
        self.output_error(post, message)

    def handle_unknown_error(self, post):
        message = 'Unknown error occurred'
        self.log_error(post, message)
        post.set_extraction_failed(message)
        self.output_error(post, message)

    def log_error(self, post, message, **kwargs):
        extra = {'post_title': post.title, 'user': post.author.name, 'subreddit': post.subreddit.name, 'url': post.url,
                 'date_posted': post.date_posted, **kwargs}
        self.logger.error(message, extra=extra, exc_info=True)

    def output_error(self, post, message):
        message = f'Failed to extract due to: {message}'
        message_extra = f'\nTitle: {post.title}\nUser: {post.author.name}\nSubreddit: {post.subreddit.name}\n' \
                        f'Url: {post.url}\n'
        self.output_queue.put(message + message_extra)
