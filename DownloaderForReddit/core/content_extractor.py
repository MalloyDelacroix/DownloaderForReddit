import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union
from queue import Empty
from praw.models import Submission, Comment as PrawComment
from bs4 import BeautifulSoup, SoupStrainer
from sqlalchemy.orm.session import Session

from ..extractors import base_extractor, direct_extractor, self_post_extractor, comment_extractor
from ..database.models import User, Subreddit, Post, Comment
from ..database.model_enums import CommentDownload
from ..utils import injector, verify_run
from ..core import const
from ..core.comment_filter import CommentFilter
from ..messaging.message import Message


class ContentExtractor:

    def __init__(self, submission_queue, download_queue, download_session_id):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.submission_queue = submission_queue
        self.download_queue = download_queue
        self.download_session_id = download_session_id
        self.output_queue = injector.get_message_queue()
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
        self.comment_filter = CommentFilter()

        self.thread_count = self.settings_manager.extraction_thread_count
        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)
        self.hold = False
        self.submit_hold = False
        self.continue_run = True

    @property
    def running(self):
        if self.hold:
            return not self.executor._work_queue.empty()
        return True
        # return not self.hold

    # def run(self):
    #     self.logger.debug('Content extractor running')
    #     while self.continue_run:
    #         item = self.submission_queue.get()
    #         if item is not None:
    #             if item == 'HOLD':
    #                 self.hold = True
    #                 self.download_queue.put('HOLD')
    #             elif item == 'RELEASE_HOLD':
    #                 self.hold = False
    #                 self.download_queue.put('RELEASE_HOLD')
    #             else:
    #                 submission = item[0]
    #                 siginificant_id = item[1]
    #                 self.handle_submission(submission, siginificant_id)
    #         else:
    #             self.continue_run = False
    #     self.download_queue.put(None)
    #     self.logger.debug('Content extractor exiting')

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
                        submission = item[0]
                        significant_id = item[1]
                        self.executor.submit(self.handle_submission, submission=submission,
                                             significant_id=significant_id)
                else:
                    self.continue_run = False
            except Empty:
                if self.submit_hold and not self.running:
                    self.download_queue.put('HOLD')
                    self.submit_hold = False
        self.executor.shutdown(wait=True)
        self.download_queue.put(None)
        self.logger.debug('Content extractor exiting')

    @verify_run
    def handle_submission(self, submission, significant_id):
        """
        Takes a reddit submission and creates a Post from its data.  Then calls the appropriate methods for the post.
        If comments are to be extracted from the submission, this is also handled here.
        :param submission: The reddit submission that is to be extracted.
        :param significant_id: The id of the reddit object for which the submissions was extracted from reddit.
        """
        with self.db.get_scoped_session() as session:
            post = self.create_post(submission, significant_id, session)
            if post is not None:
                self.handle_post(post)
            if post.significant_reddit_object.run_comment_operations:
                self.handle_comments(post, submission, session)

    @verify_run
    def handle_post(self, post):
        """
        Calls the appropriate methods for the supplied post.
        :param post: The post that is to be extracted.
        """
        if post.is_self:
            self.extract_linked_content(post)
        else:
            self.extract(post)

    @verify_run
    def create_post(self, submission: Submission, significant_id: int, session: Session) -> Optional[Post]:
        post = None
        if self.check_duplicate_post_url(submission.url, session):
            author = self.get_author(submission, session)
            subreddit = self.get_subreddit(submission, session)

            post = Post(
                title=submission.title,
                date_posted=datetime.fromtimestamp(submission.created),
                domain=submission.domain,
                score=submission.score,
                nsfw=submission.over_18,
                reddit_id=submission.id,
                url=submission.url,
                is_self=submission.is_self,
                text=submission.selftext if submission.selftext != '' else None,
                text_html=submission.selftext_html,
                extraction_date=datetime.now(),
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

    @verify_run
    def extract(self, post: Post):
        try:
            if not post.is_self:
                extractor = self.assign_extractor(post.url)(post)
            else:
                if post.significant_reddit_object.download_self_post_text:
                    extractor = self_post_extractor(post, download_session_id=self.download_session_id)
                else:
                    extractor = None
            if extractor is not None:
                extractor.extract_content()
                if not extractor.failed_extraction:
                    post.set_extracted()
                else:
                    post.set_extraction_failed(extractor.failed_extraction_message)
                for content in extractor.extracted_content:
                    self.download_queue.put(content.id)
        except TypeError:
            self.handle_unsupported_domain(post)
        except ConnectionError:
            self.handle_connection_error(post)
        except:
            self.handle_unknown_error(post)

    @verify_run
    def extract_linked_content(self, post: Post):
        """
        Extracts links from self post text by scanning the html version of the text for href tags.  After links are
        found, content is extracted the same as post content would normally be extracted, except that the process is
        done for each link found.
        :param post: The post who's text content is to be scanned for links.
        """
        if post.significant_reddit_object.extract_self_post_links:
            failed = False
            links = BeautifulSoup(post.text_html, parse_only=SoupStrainer('a'), features='html.parser')
            track_count = len(links) > 1
            for link in links:
                if link.has_attr('href'):
                    url = link['href']
                    title = post.title
                    count = links.index(link) + 1 if track_count else None
                    try:
                        extractor_class = self.assign_extractor(url)
                        extractor = extractor_class(post, url=url, count=count)
                        extractor.extract_content()
                        if extractor.failed_extraction:
                            failed = True
                        for content in extractor.extracted_content:
                            self.download_queue.put(content.id)
                    except TypeError:
                        self.handle_unsupported_domain(post, url=url, title=title)
                    except ConnectionError:
                        self.handle_connection_error(post, url=url, title=title)
                    except:
                        self.handle_unknown_error(post, url=url, title=title)
            if failed:
                post.set_extraction_failed('Failed to extract one or more links from text')
            else:
                post.set_extracted()

    @verify_run
    def handle_comments(self, post: Post, submission: Submission, session: Session):
        significant_ro = post.significant_reddit_object
        sort_method = significant_ro.comment_sort_method
        if sort_method.value == 6:
            sort_method = 'q&a'
        else:
            sort_method = sort_method.name.lower()
        submission.comment_sort = sort_method
        submission.comments.replace_more(limit=0)
        for praw_comment in submission.comments[: significant_ro.comment_limit]:
            self.cascade_comments(praw_comment, post, session)

    @verify_run
    def cascade_comments(self, praw_comment: PrawComment, post: Post, session: Session,
                         parent_id: Optional[int] = None):
        significant_ro = post.significant_reddit_object
        if self.comment_filter.filter_extraction(praw_comment, significant_ro) and \
                self.comment_filter.filter_score_limit(praw_comment, significant_ro):
            comment = self.create_comment(praw_comment, post, session, parent_comment_id=parent_id)
            if comment is not None:
                if self.comment_filter.filter_download(praw_comment, significant_ro):
                    self.extract_comment_text(comment)
                if self.comment_filter.filter_content_download(praw_comment, significant_ro):
                    self.extract_comment_content(comment)

                praw_comment.replies.replace_more(limit=0)
                for sub_comment in praw_comment.replies:
                    self.cascade_comments(sub_comment, post, session, parent_id=comment.id)

    @verify_run
    def extract_comment_text(self, comment):
        extractor = comment_extractor(post=comment.post, comment=comment, download_session_id=self.download_session_id)
        extractor.extract_content()

    @verify_run
    def handle_comment_content(self, comment: Comment):
        download_type = comment.post.significant_reddit_object.download_comment_content
        if (download_type == CommentDownload.DOWNLOAD_ONLY_AUTHOR and comment.author_id == comment.post.author_id) or \
                download_type == CommentDownload.DOWNLOAD:
            self.extract_comment_content(comment)

    @verify_run
    def extract_comment_content(self, comment: Comment):
        failed = False
        links = BeautifulSoup(comment.body_html, parse_only=SoupStrainer('a'), features='html.parser')
        links_size = len(links)
        if links_size > 0:
            comment.has_content = True
        track_count = links_size > 1
        for link in links:
            if link.has_attr('href'):
                url = link['href']
                count = links.index(link) + 1 if track_count else None
                try:
                    extractor_class = self.assign_extractor(url)
                    extractor = extractor_class(comment.post, comment=comment, count=count, author=comment.author,
                                                subreddit=comment.subreddit, url=url, date_posted=comment.date_posted)
                    extractor.extract_content()
                    if extractor.failed_extraction:
                        failed = True
                    for content in extractor.extracted_content:
                        self.download_queue.put(content.id)
                except TypeError:
                    self.handle_unsupported_domain(comment.post, url=url, comment_author=comment.author,
                                                   comment_id=comment.id)
                except ConnectionError:
                    self.handle_connection_error(comment.post, url=url, comment_author=comment.author,
                                                 comment_id=comment.id)
                except:
                    self.handle_unknown_error(comment.post, url=url, comment_author=comment.author,
                                              comment_id=comment.id)
        if failed:
            comment.set_extraction_failed('Failed to extract one or more links from text body')
        else:
            comment.set_extracted()

    def create_comment(self, praw_comment: PrawComment, post: Post, session: Session,
                       parent_comment_id: Optional[int] = None):
        if self.check_duplicate_comment(praw_comment.id, session):
            author = self.get_author(praw_comment, session)
            subreddit = self.get_subreddit(praw_comment, session)
            comment = Comment(
                author=author,
                subreddit=subreddit,
                post=post,
                reddit_id=praw_comment.id,
                body=praw_comment.body,
                body_html=praw_comment.body_html,
                score=praw_comment.score,
                date_posted=datetime.fromtimestamp(praw_comment.created),
                parent_id=parent_comment_id,
                download_session_id=self.download_session_id
            )
            session.add(comment)
            session.commit()
            return comment
        return None

    def check_duplicate_comment(self, comment_id: str, session: Session):
        return session.query(Comment).filter(Comment.reddit_id == comment_id).scalar() is None

    def get_author(self, praw_object: Union[Submission, PrawComment], session: Session):
        try:
            author = self.db.get_or_create(User, name=praw_object.author.name,
                                           date_created=self.get_created(praw_object.author), session=session)[0]
        except AttributeError:
            author = self.db.get_or_create(User, name='deleted', session=session)[0]
        return author

    def get_subreddit(self, praw_object: Union[Submission, PrawComment], session: Session):
        try:
            subreddit = self.db.get_or_create(Subreddit, name=praw_object.subreddit.display_name,
                                              date_created=self.get_created(praw_object.subreddit),
                                              session=session)[0]
        except AttributeError:
            subreddit = self.db.get_or_create(Subreddit, name='deleted', session=session)[0]
        return subreddit

    def get_created(self, praw_object):
        try:
            return datetime.fromtimestamp(praw_object.created)
        except:
            self.logger.error('Failed to get creation date for reddit object', exc_info=True)

    def assign_extractor(self, url):
        for extractor in base_extractor.__subclasses__():
            key = extractor.get_url_key()
            if key is not None and any(x in url.lower() for x in key):
                return extractor
        if url.lower().endswith(const.ALL_EXT):
            return direct_extractor
        return None

    def run_unextracted_posts(self):
        """
        Queries the database for posts that were not extracted (either due to connection error or user interference with
        download) and attempts to re-extract and download them.
        """
        self.logger.debug('Content extractor running un-extracted posts')
        with self.db.get_scoped_session() as session:
            unfinished_posts = session.query(Post.id)\
                .filter(Post.extracted == False)\
                .filter(Post.extraction_error == None)
            for post_id in unfinished_posts:
                self.executor.submit(self.finish_post, post_id)
        self.executor.shutdown(wait=True)
        self.download_queue.put(None)
        self.logger.debug('Content extractor finished un-extracted posts, now exiting')

    def finish_post(self, post_id):
        with self.db.get_scoped_session() as session:
            post = session.query(Post).get(post_id)
            self.handle_post(post)

    def handle_unsupported_domain(self, post, **kwargs):
        message = 'Unsupported domain'
        self.log_error(post, message, **kwargs)
        post.set_extraction_failed(message)
        self.output_error(post, message, **kwargs)

    def handle_connection_error(self, post, **kwargs):
        message = 'Failed to establish a connection to the server'
        self.log_error(post, message, **kwargs)
        post.set_extraction_failed(message)
        self.output_error(post, message, **kwargs)

    def handle_unknown_error(self, post, **kwargs):
        message = 'Unknown error occurred'
        self.log_error(post, message, **kwargs)
        post.set_extraction_failed(message)
        self.output_error(post, message, **kwargs)

    def log_error(self, post, message, **kwargs):
        extra = {'post_title': post.title, 'user': post.author.name, 'subreddit': post.subreddit.name, 'url': post.url,
                 'date_posted': post.date_posted, **kwargs}
        self.logger.error(message, extra=extra, exc_info=True)

    def output_error(self, post, message, **kwargs):
        message = f'Failed to extract due to: {message}'
        message_extra = f'\nTitle: {post.title}\nUser: {post.author.name}\nSubreddit: {post.subreddit.name}\n' \
                        f'Url: {kwargs.get("url", post.url)}\n'
        Message.send_extraction_error(message + message_extra)
