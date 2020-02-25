from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from .DatabaseHandler import DatabaseHandler
from .ModelEnums import DownloadNameMethod, SubredditSaveStructure
from ..Core import Const


Base = DatabaseHandler.base

list_association = Table(
    'reddit_object_list_assoc', Base.metadata,
    Column('list_id', Integer, ForeignKey('reddit_object_lists.id')),
    Column('reddit_object_id', Integer, ForeignKey('reddit_objects.id'))
)


class RedditObjectList(Base):

    __tablename__ = 'reddit_object_lists'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    date_created = Column(DateTime, default=datetime.now())
    list_type = Column(String, nullable=False)
    reddit_objects = relationship('RedditObject', secondary=list_association, backref='lists', lazy='dynamic')


class RedditObject(Base):

    __tablename__ = 'reddit_objects'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    post_limit = Column(SmallInteger, default=25)
    avoid_duplicates = Column(Boolean, default=True)
    download_videos = Column(Boolean, default=True)
    download_images = Column(Boolean, default=True)
    download_nsfw = Column(Integer, default=0)  # -1 = exclude | 0 = include | 1 = only include
    date_added = Column(DateTime, default=datetime.now())
    lock_settings = Column(Boolean, default=False)
    absolute_date_limit = Column(DateTime, default=datetime.fromtimestamp(Const.FIRST_POST_EPOCH))
    date_limit = Column(DateTime, nullable=True)
    download_enabled = Column(Boolean, default=True)
    last_download = Column(DateTime, nullable=True)
    significant = Column(Boolean, default=False)
    post_sort_method = Column(String, default='NEW')
    download_naming_method = Column(Enum(DownloadNameMethod), default=DownloadNameMethod.title)
    subreddit_save_structure = Column(Enum(SubredditSaveStructure), default=SubredditSaveStructure.sub_name)
    new = Column(Boolean, default=True)

    object_type = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity': 'REDDIT_OBJECT',
        'polymorphic_on':  object_type,
    }

    def toggle_enable_download(self):
        self.download_enabled = not self.download_enabled
        Session.object_session(self).commit()


class User(RedditObject):

    __tablename__ = 'users'

    id = Column(ForeignKey('reddit_objects.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'USER',
    }


class Subreddit(RedditObject):

    __tablename__ = 'subreddits'

    id = Column(ForeignKey('reddit_objects.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'SUBREDDIT',
    }


class Post(Base):

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_posted = Column(DateTime)
    domain = Column(String)
    score = Column(Integer)
    nsfw = Column(Boolean, default=False)
    reddit_id = Column(String)
    extraction_date = Column(DateTime, nullable=True)
    url = Column(String)

    author_id = Column(ForeignKey('users.id'))
    author = relationship('User', backref='posts')
    subreddit_id = Column(ForeignKey('subreddits.id'))
    subreddit = relationship('Subreddit', backref='posts')


class Comment(Base):

    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    body = Column(String)
    body_html = Column(String)
    score = Column(Integer)
    date_added = Column(DateTime, default=datetime.now())
    date_posted = Column(DateTime)

    author_id = ForeignKey('users.id')
    author = relationship('User', backref='comments')
    subreddit_id = ForeignKey('subreddits.id')
    subreddit = relationship('Subreddit', backref='comments')
    post_id = ForeignKey('posts.id')
    post = ForeignKey('Post', backref='comments')
    parent_id = ForeignKey('comments.id', nullable=True)
    parent = relationship('Comment', remote_side=[id], backref='children', nullable=True)


class Content(Base):

    __tablename__ = 'content'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    download_date = Column(DateTime, nullable=True)
    extension = Column(String)
    url = Column(String)

    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', backref='content')
    subreddit_id = Column(ForeignKey('subreddits.id'))
    subreddit = relationship('Subreddit', backref='content')
    post_id = Column(ForeignKey('posts.id'))
    post = relationship('Post', backref='content')
