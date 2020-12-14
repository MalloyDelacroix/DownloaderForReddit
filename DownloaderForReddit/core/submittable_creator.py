import logging
from datetime import datetime
from typing import Optional, Union
from sqlalchemy.orm.session import Session
from praw.models import Submission, Comment as PrawComment

from ..database.models import User, Subreddit, Post, Comment
from ..utils import injector


class SubmittableCreator:

    logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
    db = injector.get_database_handler()

    @classmethod
    def create_post(cls, submission: Submission, significant_id: int, session: Session, download_session_id: int) \
            -> Optional[Post]:
        post = None
        if cls.check_duplicate_post_url(submission.url, session):
            author = cls.get_author(submission, session)
            subreddit = cls.get_subreddit(submission, session)

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
                download_session_id=download_session_id,
                significant_reddit_object_id=significant_id
            )
            session.add(post)
            session.commit()
        return post

    @classmethod
    def check_duplicate_post_url(cls, url, session):
        return session.query(Post.id).filter(Post.url == url).scalar() is None

    @classmethod
    def create_comment(cls, praw_comment: PrawComment, post: Post, session: Session, download_session_id: int,
                       parent_comment_id: Optional[int] = None):
        if cls.check_duplicate_comment(praw_comment.id, session):
            author = cls.get_author(praw_comment, session)
            subreddit = cls.get_subreddit(praw_comment, session)
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
                download_session_id=download_session_id
            )
            session.add(comment)
            session.commit()
            return comment
        return None

    @classmethod
    def check_duplicate_comment(cls, praw_comment_id: str, session: Session):
        return session.query(Comment).filter(Comment.reddit_id == praw_comment_id).scalar() is None

    @classmethod
    def get_author(cls, praw_object: Union[Submission, PrawComment], session: Session):
        try:
            defaults = {}
            date_created = cls.get_created(praw_object.author)
            if date_created is None:
                defaults = {'date_created': None, 'active': False, 'inactive_date': datetime.now()}
            author = cls.db.get_or_create(User, name=praw_object.author.name, defaults=defaults, session=session)[0]
        except AttributeError:
            author = cls.db.get_or_create(User, name='deleted', session=session)[0]
        return author

    @classmethod
    def get_subreddit(cls, praw_object: Union[Submission, PrawComment], session: Session):
        try:
            defaults = {}
            date_created = cls.get_created(praw_object.subreddit)
            if date_created is None:
                defaults = {'date_created': None, 'active': False, 'inactive_date': datetime.now()}
            subreddit = cls.db.get_or_create(Subreddit, name=praw_object.subreddit.display_name, defaults=defaults,
                                             session=session)[0]
        except AttributeError:
            subreddit = cls.db.get_or_create(Subreddit, name='deleted', session=session)[0]
        return subreddit

    @classmethod
    def get_created(cls, praw_object):
        try:
            return datetime.fromtimestamp(praw_object.created)
        except:
            return None
