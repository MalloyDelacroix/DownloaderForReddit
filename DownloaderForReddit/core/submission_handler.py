import logging
from typing import Optional
from queue import Queue
from praw.models import Submission
from sqlalchemy.orm.session import Session
from bs4 import BeautifulSoup, SoupStrainer

from .runner import Runner, verify_run
from .comment_handler import CommentHandler
from .errors import Error
from . import const
from ..database.models import Post
from ..extractors.base_extractor import BaseExtractor
from ..extractors.direct_extractor import DirectExtractor
from ..extractors.self_post_extractor import SelfPostExtractor
from ..extractors.comment_extractor import CommentExtractor
from ..messaging.message import Message
from ..utils import injector


class SubmissionHandler(Runner):

    def __init__(self, submission: Optional[Submission], post: Post, download_session_id: int, session: Session,
                 download_queue: Queue, stop_run):
        super().__init__(stop_run)
        self.logger = logging.getLogger(__name__)
        self.settings_manager = injector.get_settings_manager()
        self.submission = submission
        self.post = post
        self.download_session_id = download_session_id
        self.session = session
        self.download_queue = download_queue

        self.content = []

    @verify_run
    def extract_submission(self):
        if not self.submission.is_self:
            self.extract_submission_content()
        else:
            self.extract_self_post()

    @verify_run
    def extract_submission_content(self):
        self.extract_link(self.post.url)

    @verify_run
    def extract_self_post(self):
        significant_ro = self.post.significant_reddit_object
        if significant_ro.download_self_post_text:
            try:
                extractor = SelfPostExtractor(self.post, download_session_id=self.download_session_id)
                self.finish_extractor(extractor)
                if self.post.significant_reddit_object.extract_self_post_links:
                    self.extract_text_links(self.post.text_html)
            except Exception as e:
                self.handle_error(e)

    @verify_run
    def extract_comments(self):
        comment_handler = CommentHandler(self.submission, self.post, self.download_session_id, self.stop_run,
                                         self.session)
        comment_handler.run()
        for comment in comment_handler.comments_to_download:
            self.download_comment(comment)
        for comment in comment_handler.comments_to_extract_links:
            self.extract_text_links(comment.body_html, comment=comment, user=comment.author,
                                    subreddit=comment.subreddit,
                                    significant_reddit_object=self.post.significant_reddit_object,
                                    creation_date=comment.date_posted)

    @verify_run
    def download_comment(self, comment):
        extractor = CommentExtractor(post=self.post, comment=comment, download_session_id=self.download_session_id)
        self.finish_extractor(extractor, text_link_extraction=True, comment=comment)

    @verify_run
    def extract_text_links(self, html_text, **kwargs):
        links = self.parse_html_links(html_text)
        track_count = len(links) > 1
        for link in links:
            if link.has_attr('href'):
                url = link['href']
                if track_count:
                    kwargs['count'] = links.index(link) + 1
                self.extract_link(url, **kwargs, text_link_extraction=True)

    def parse_html_links(self, html):
        return BeautifulSoup(html, parse_only=SoupStrainer('a'), features='html.parser')

    @verify_run
    def extract_link(self, url, text_link_extraction=False, **kwargs):
        try:
            extractor_class = self.assign_extractor(url)
            extractor = extractor_class(self.post, url=url, submission=self.submission, **kwargs)
            self.finish_extractor(extractor, text_link_extraction=text_link_extraction)
        except Exception as e:
            self.handle_error(e)

    @verify_run
    def finish_extractor(self, extractor, text_link_extraction=False, comment=None):
        if extractor is not None:
            extractor.extract_content()
            if not extractor.failed_extraction:
                self.post.set_extracted()
            else:
                if not text_link_extraction:
                    self.post.set_extraction_failed(extractor.extraction_error, extractor.failed_extraction_message)
                else:
                    if comment is None:
                        self.post.set_extraction_failed(Error.TEXT_LINK_FAILURE,
                                                        'Failed to extract link from text post')
                    else:
                        comment.set_extraction_failed(Error.TEXT_LINK_FAILURE,
                                                      'Failed to extract links from comment text')
            for content in extractor.extracted_content:
                self.download_queue.put(content.id)

    @verify_run
    def assign_extractor(self, url):
        for extractor in BaseExtractor.__subclasses__():
            if self.settings_manager.extractor_dict[extractor.__name__]:
                key = extractor.get_url_key()
                if key is not None and any(x in url.lower() for x in key):
                    return extractor
        if url.lower().endswith(const.ALL_EXT) and self.settings_manager.extractor_dict['DirectExtractor']:
            return DirectExtractor
        return None

    def handle_error(self, exception):
        if isinstance(exception, TypeError):
            self.handle_unsupported_domain()
        elif isinstance(exception, ConnectionError):
            self.handle_connection_error()
        else:
            self.handle_unknown_error()

    def handle_unsupported_domain(self, **kwargs):
        message = 'Unsupported domain'
        self.log_error(message, **kwargs)
        self.post.set_extraction_failed(Error.UNSUPPORTED_DOMAIN, message)
        self.output_error(message, **kwargs)

    def handle_connection_error(self, **kwargs):
        message = 'Failed to establish a connection to the server'
        self.log_error(message, **kwargs)
        self.post.set_extraction_failed(Error.CONNECTION_ERROR, message)
        self.output_error(message, **kwargs)

    def handle_unknown_error(self, **kwargs):
        message = 'Unknown error occurred'
        self.log_error(message, **kwargs)
        self.post.set_extraction_failed(Error.UNKNOWN_ERROR, message)
        self.output_error(message, **kwargs)

    def log_error(self, message, **kwargs):
        extra = {'post_title': self.post.title, 'user': self.post.author.name,
                 'subreddit': self.post.subreddit.name, 'url': self.post.url,
                 'date_posted': self.post.date_posted, **kwargs}
        self.logger.error(message, extra=extra, exc_info=True)

    def output_error(self, message, **kwargs):
        message = f'Failed to extract due to: {message}'
        message_extra = f'\nTitle: {self.post.title}\nUser: {self.post.author.name}\n' \
                        f'Subreddit: {self.post.subreddit.name}\nUrl: {kwargs.get("url", self.post.url)}\n'
        Message.send_extraction_error(message + message_extra)
