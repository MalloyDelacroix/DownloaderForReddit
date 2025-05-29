from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, DateTime, ForeignKey, Text, Enum, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import func

from .database_handler import DatabaseHandler
from .model_enums import (CommentDownload, NsfwFilter, LimitOperator, PostSortMethod, CommentSortMethod)
from ..core.errors import Error
from ..core import const
from ..utils import system_util, injector, general_utils


Base = DatabaseHandler.base


class BaseModel(Base):

    __abstract__ = True

    def get_session(self):
        return Session.object_session(self)

    def save(self):
        self.get_session().commit()

    def get_display_datetime(self, date_time):
        try:
            return general_utils.format_datetime(date_time)
        except AttributeError:
            return None

    def get_display_date(self, date):
        try:
            return general_utils.format_date(date)
        except AttributeError:
            return None

    def get_path_datetime(self, date_time):
        try:
            return general_utils.format_date_path(self.get_display_datetime(date_time))
        except AttributeError:
            return None

    def get_path_date(self, date):
        try:
            return general_utils.format_date_path(self.get_display_date(date))
        except AttributeError:
            return None


class Version(BaseModel):

    __tablename__ = 'version'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, default='0.0.0')
    date_added = Column(DateTime, default=datetime.now())


class ListAssociation(BaseModel):

    __tablename__ = 'reddit_object_list_association'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reddit_object_list_id = Column(ForeignKey('reddit_object_list.id'))
    reddit_object_list = relationship('RedditObjectList', backref=backref('list_subscriptions',
                                                                          cascade='all, delete-orphan'))
    reddit_object_id = Column(ForeignKey('reddit_object.id'))
    reddit_object = relationship('RedditObject', backref=backref('list_subscriptions', cascade='all, delete-orphan'))
    date_added = Column(DateTime, default=datetime.now())


class RedditObjectList(BaseModel):

    __tablename__ = 'reddit_object_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(collation='NOCASE'))
    date_created = Column(DateTime, default=datetime.now())
    list_type = Column(String, nullable=False)
    reddit_objects = relationship('RedditObject', secondary='reddit_object_list_association', lazy='dynamic')

    # region List Download Defaults
    lock_settings = Column(Boolean, default=False)
    post_limit = Column(SmallInteger, default=25)
    post_score_limit = Column(Integer, default=1000)
    post_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    post_sort_method = Column(Enum(PostSortMethod), default=PostSortMethod.NEW)
    avoid_duplicates = Column(Boolean, default=True)
    extract_self_post_links = Column(Boolean, default=False)
    download_self_post_text = Column(Boolean, default=False)
    self_post_file_format = Column(String, default='txt')
    download_videos = Column(Boolean, default=True)
    download_images = Column(Boolean, default=True)
    download_gifs = Column(Boolean, default=True)
    download_nsfw = Column(Enum(NsfwFilter), default=NsfwFilter.INCLUDE)

    extract_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comment_content = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    comment_file_format = Column(String, default='txt')
    comment_limit = Column(Integer, default=100)
    comment_depth = Column(Integer, default=100)
    comment_reply_limit = Column(Integer, default=100)
    comment_score_limit = Column(Integer, default=1000)
    comment_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    comment_sort_method = Column(Enum(CommentSortMethod), default=CommentSortMethod.NEW)

    date_limit = Column(DateTime, nullable=True)
    update_date_limit = Column(Boolean, default=True)
    post_download_naming_method = Column(String, default='%[title]')
    post_save_structure = Column(String, default='%[author_name]')
    custom_post_save_path = Column(String, nullable=True)
    comment_naming_method = Column(String, default='%[author_name]-comment')
    comment_save_structure = Column(String, default='%[post_author_name]/Comments/%[post_title]')
    custom_comment_save_path = Column(String, nullable=True)
    # endregion

    object_type = 'REDDIT_OBJECT_LIST'
    download_enabled = True
    absolute_date_limit = None
    updated = False

    def __str__(self):
        return f'{self.list_type} List: {self.name}'

    @property
    def display_name(self):
        return f'{self.name} [{self.list_type}]'

    @property
    def date_created_display(self):
        return self.get_display_datetime(self.date_created)

    @property
    def date_created_export(self):
        return self.get_display_datetime(self.date_created)

    @property
    def date_limit_display(self):
        return self.get_display_datetime(self.date_limit)

    @property
    def date_limit_export(self):
        return self.get_display_datetime(self.date_limit)

    @property
    def absolute_date_limit_display(self):
        return self.get_display_datetime(self.absolute_date_limit)

    @property
    def absolute_date_limit_export(self):
        return self.get_display_datetime(self.absolute_date_limit)

    def get_reddit_object_id_list(self):
        return [x.id for x in self.reddit_objects]

    def get_reddit_object_sub(self, session):
        return session.query(ListAssociation.reddit_object_id).filter(ListAssociation.reddit_object_list_id == self.id)

    def get_post_count(self, session=None):
        if session is None:
            session = self.get_session()
        sub = self.get_reddit_object_sub(session)
        return session.query(func.count(Post.id)).filter(Post.significant_reddit_object_id.in_(sub)).scalar()

    def get_content_count(self, session=None):
        if session is None:
            session = self.get_session()
        sub = self.get_reddit_object_sub(session)
        return session.query(func.count(Content.id)).join(Post)\
            .filter(Post.significant_reddit_object_id.in_(sub)).scalar()

    def get_comment_count(self, session=None):
        if session is None:
            session = self.get_session()
        sub = self.get_reddit_object_sub(session)
        return session.query(func.count(Comment.id)).join(Post)\
            .filter(Post.significant_reddit_object_id.in_(sub)).scalar()

    def get_default_dict(self):
        return {
            'lock_settings': self.lock_settings,
            'post_limit': self.post_limit,
            'post_score_limit': self.post_score_limit,
            'post_score_limit_operator': self.post_score_limit_operator,
            'post_sort_method': self.post_sort_method,
            'avoid_duplicates': self.avoid_duplicates,
            'extract_self_post_links': self.extract_self_post_links,
            'download_self_post_text': self.download_self_post_text,
            'self_post_file_format': self.self_post_file_format,
            'download_videos': self.download_videos,
            'download_images': self.download_images,
            'download_gifs': self.download_gifs,
            'download_nsfw': self.download_nsfw,
            'extract_comments': self.extract_comments,
            'download_comments': self.download_comments,
            'download_comment_content': self.download_comment_content,
            'comment_file_format': self.comment_file_format,
            'comment_limit': self.comment_limit,
            'comment_depth': self.comment_depth,
            'comment_reply_limit': self.comment_reply_limit,
            'comment_score_limit': self.comment_score_limit,
            'comment_score_limit_operator': self.comment_score_limit_operator,
            'comment_sort_method': self.comment_sort_method,
            'date_limit': self.date_limit,
            'update_date_limit': self.update_date_limit,
            'post_download_naming_method': self.post_download_naming_method,
            'post_save_structure': self.post_save_structure,
            'custom_post_save_path': self.custom_post_save_path,
            'comment_naming_method': self.comment_naming_method,
            'comment_save_structure': self.comment_save_structure,
            'custom_comment_save_path': self.custom_comment_save_path,
        }

    def sync_reddit_object_settings(self, reddit_object):
        for key, value in self.get_default_dict().items():
            setattr(reddit_object, key, value)


class RedditObject(BaseModel):

    __tablename__ = 'reddit_object'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(collation='NOCASE'))
    date_created = Column(DateTime, nullable=True)
    post_limit = Column(SmallInteger, default=25)
    post_score_limit = Column(Integer, default=1000)
    post_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    post_sort_method = Column(Enum(PostSortMethod), default=PostSortMethod.NEW)
    avoid_duplicates = Column(Boolean, default=True)
    extract_self_post_links = Column(Boolean, default=False)
    download_self_post_text = Column(Boolean, default=False)
    self_post_file_format = Column(String, default='txt')
    download_videos = Column(Boolean, default=True)
    download_images = Column(Boolean, default=True)
    download_gifs = Column(Boolean, default=True)
    download_nsfw = Column(Enum(NsfwFilter), default=NsfwFilter.INCLUDE)

    extract_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comments = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    download_comment_content = Column(Enum(CommentDownload), default=CommentDownload.DO_NOT_DOWNLOAD)
    comment_file_format = Column(String, default='txt')
    comment_limit = Column(Integer, default=100)
    comment_depth = Column(Integer, default=100)
    comment_reply_limit = Column(Integer, default=100)
    comment_score_limit = Column(Integer, default=1000)
    comment_score_limit_operator = Column(Enum(LimitOperator), default=LimitOperator.NO_LIMIT)
    comment_sort_method = Column(Enum(CommentSortMethod), default=CommentSortMethod.NEW)

    date_added = Column(DateTime, default=datetime.now())
    lock_settings = Column(Boolean, default=False)
    absolute_date_limit = Column(DateTime, default=datetime.fromtimestamp(const.FIRST_POST_EPOCH))
    date_limit = Column(DateTime, nullable=True)
    update_date_limit = Column(Boolean, default=True)
    download_enabled = Column(Boolean, default=True)
    significant = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    inactive_date = Column(DateTime, nullable=True)
    post_download_naming_method = Column(String, default='%[title]')
    post_save_structure = Column(String, default='%[author_name]')
    custom_post_save_path = Column(String, nullable=True)
    comment_naming_method = Column(String, default='%[author_name]-comment')
    comment_save_structure = Column(String, default='%[post_author_name]/Comments/%[post_title]')
    custom_comment_save_path = Column(String, nullable=True)
    new = Column(Boolean, default=True)
    lists = relationship(RedditObjectList, secondary='reddit_object_list_association', lazy='dynamic')

    object_type = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity': 'REDDIT_OBJECT',
        'polymorphic_on':  object_type,
    }

    def __str__(self):
        try:
            return f'{self.object_type}: {self.name}'
        except AttributeError:
            return f'{self.object_type}: {self.id}'

    @property
    def date_created_display(self):
        return self.get_display_datetime(self.date_created)

    @property
    def date_created_export(self):
        return self.get_display_datetime(self.date_created)

    @property
    def date_added_display(self):
        return self.get_display_datetime(self.date_added)

    @property
    def date_added_export(self):
        return self.get_display_datetime(self.date_added)

    @property
    def absolute_date_limit_display(self):
        return self.get_display_datetime(self.absolute_date_limit)

    @property
    def absolute_date_limit_export(self):
        return self.get_display_datetime(self.absolute_date_limit)

    @property
    def date_limit_display(self):
        return self.get_display_datetime(self.date_limit)

    @property
    def date_limit_export(self):
        return self.get_display_datetime(self.date_limit)

    @property
    def last_download(self):
        return self.get_session().query(func.max(Content.download_date)).join(Post)\
            .filter(Post.significant_reddit_object_id == self.id).first()[0]

    @property
    def last_download_display(self):
        return self.get_display_datetime(self.last_download)

    @property
    def last_download_export(self):
        return self.get_display_datetime(self.last_download)

    @property
    def inactive_date_display(self):
        return self.get_display_datetime(self.inactive_date)

    @property
    def inactive_date_export(self):
        return self.get_display_datetime(self.inactive_date)

    @property
    def run_comment_operations(self):
        return any((self.extract_comments != CommentDownload.DO_NOT_DOWNLOAD,
                    self.download_comments != CommentDownload.DO_NOT_DOWNLOAD,
                    self.download_comment_content != CommentDownload.DO_NOT_DOWNLOAD))

    @property
    def total_score(self):
        score = self.get_session().query(func.sum(Post.score))\
            .filter(Post.significant_reddit_object_id == self.id).first()[0]
        if score is None:
            score = 0
        return score

    @property
    def total_score_display(self):
        return '{:,}'.format(self.total_score)

    @property
    def post_count(self):
        return len(self.posts)

    @property
    def content_count(self):
        return len(self.content)

    @property
    def comment_count(self):
        return len(self.comments)

    @property
    def list_count(self):
        return self.lists.count()

    @property
    def used(self):
        return self.list_count > 0

    def set_existing(self):
        if self.new:
            self.new = False
            self.get_session().commit()

    def set_date_limit(self, epoch):
        """
        Tests the supplied epoch time to see if it is newer than the already established absolute date limit, and if so
        sets the absolute date limit to the time of the supplied epoch.
        :param epoch: A datetime in epoch seconds that should be the time of an extracted submission.
        """
        date_limit_epoch = self.absolute_date_limit.timestamp()
        if epoch > date_limit_epoch:
            self.absolute_date_limit = datetime.fromtimestamp(epoch)
            if self.update_date_limit:
                self.date_limit = None
            self.get_session().commit()

    def set_inactive(self, commit=True):
        self.active = False
        self.inactive_date = datetime.now()
        if commit:
            self.get_session().commit()
        return True

    def toggle_enable_download(self):
        self.download_enabled = not self.download_enabled
        self.get_session().commit()

    def get_stats(self):
        session = self.get_session()
        return {
            'lists': session.query(ListAssociation).filter(ListAssociation.reddit_object_id == self.id).count(),
            'posts': self.post_count,
            'content': self.content_count,
            'comments': self.comment_count
        }


class User(RedditObject):

    __tablename__ = 'user'

    id = Column(ForeignKey('reddit_object.id'), primary_key=True, autoincrement=True)

    __mapper_args__ = {
        'polymorphic_identity': 'USER',
    }


class Subreddit(RedditObject):

    __tablename__ = 'subreddit'

    id = Column(ForeignKey('reddit_object.id'), primary_key=True, autoincrement=True)

    __mapper_args__ = {
        'polymorphic_identity': 'SUBREDDIT',
    }


class DownloadSession(BaseModel):

    __tablename__ = 'download_session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(collation='NOCASE'), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    extraction_thread_count = Column(Integer, nullable=True)
    download_thread_count = Column(Integer, nullable=True)

    def __str__(self):
        return f'DownloadSession: {self.id}'

    @property
    def start_time_display(self):
        return self.get_display_datetime(self.start_time)

    @property
    def start_time_export(self):
        return self.get_display_datetime(self.start_time)

    @property
    def end_time_display(self):
        return self.get_display_datetime(self.end_time)

    @property
    def end_time_export(self):
        return self.get_display_datetime(self.end_time)

    @property
    def duration_display(self):
        try:
            return system_util.format_duration_full(self.duration)
        except AttributeError:
            return 'Never finished'

    def get_downloaded_reddit_object_count(self, session=None):
        if session is None:
            session = self.get_session()
        return session.query(Post.significant_reddit_object_id)\
            .filter(Post.download_session_id == self.id).distinct().count()

    def get_downloaded_user_count(self, significant=True, session=None):
        if session is None:
            session = self.get_session()
        if significant:
            query = session.query(Post.significant_reddit_object_id) \
                .filter(Post.author_id == Post.significant_reddit_object_id)
        else:
            query = session.query(Post.subreddit_id)
        return query.filter(Post.download_session_id == self.id).distinct().count()

    def get_downloaded_subreddit_count(self, significant=True, session=None):
        if session is None:
            session = self.get_session()
        if significant:
            query = session.query(Post.significant_reddit_object_id)\
                .filter(Post.subreddit_id == Post.significant_reddit_object_id)
        else:
            query = session.query(Post.author_id)
        return query.filter(Post.download_session_id == self.id).distinct().count()

    def get_extracted_post_count(self, session=None):
        if session is None:
            session = self.get_session()
        return session.query(Post.id).filter(Post.download_session_id == self.id).count()

    def get_downloaded_content_count(self, session=None):
        if session is None:
            session = self.get_session()
        return session.query(Content.id).filter(Content.download_session_id == self.id).count()

    def get_comment_count(self, session=None):
        if session is None:
            session = self.get_session()
        return session.query(Comment.id).filter(Comment.download_session_id == self.id).count()

    def get_downloaded_reddit_objects(self, session=None):
        if session is None:
            session = self.get_session()
        subquery = session.query(Post.significant_reddit_object_id).filter(Post.download_session_id == self.id)
        return session.query(RedditObject).filter(RedditObject.id.in_(subquery))


@event.listens_for(DownloadSession.end_time, 'set')
def set_download_session_duration(target, value, oldValue, initiator):
    target.duration = value.timestamp() - target.start_time.timestamp()


@event.listens_for(DownloadSession, 'before_insert')
def set_download_session_name(mapper, connection, target):
    if target.name is None:
        try:
            number = target.get_session().query(DownloadSession.id).order_by(DownloadSession.id.desc()).first()[0] + 1
        except TypeError:
            number = 1
        target.name = f'Download Session {number}'


class Post(BaseModel):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(collation='NOCASE'))
    date_posted = Column(DateTime)
    domain = Column(String(collation='NOCASE'))
    score = Column(Integer)
    nsfw = Column(Boolean, default=False)
    reddit_id = Column(String(collation='NOCASE'), unique=True)
    url = Column(String)

    is_self = Column(Boolean, default=False)
    text = Column(Text, nullable=True)
    text_html = Column(Text, nullable=True)

    extracted = Column(Boolean, default=False)
    extraction_date = Column(DateTime, nullable=True)
    extraction_error = Column(Enum(Error), nullable=True)
    error_message = Column(String, nullable=True)
    retry_attempts = Column(Integer, default=0)

    author_id = Column(ForeignKey('user.id'))
    author = relationship('User', foreign_keys=author_id, backref='posts')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', foreign_keys=subreddit_id, backref='posts')
    significant_reddit_object_id = Column(ForeignKey('reddit_object.id'))
    significant_reddit_object = relationship('RedditObject', foreign_keys=significant_reddit_object_id,
                                             backref='significant_posts')
    download_session_id = Column(ForeignKey('download_session.id'))
    download_session = relationship('DownloadSession', backref='posts')  # session where the post was extracted

    def __str__(self):
        return f'Post: {self.title}'

    @property
    def short_title(self):
        length = injector.get_settings_manager().short_title_char_length
        if length > 0:
            return self.title[:length]
        else:
            return self.title

    @property
    def sanitized_title(self):
        return system_util.clean(self.title)

    @property
    def sanitized_short_title(self):
        return system_util.clean(self.short_title)

    @property
    def date_posted_display(self):
        return self.get_display_datetime(self.date_posted)

    @property
    def date_posted_export(self):
        return self.get_display_datetime(self.date_posted)

    @property
    def date_posted_path(self):
        return self.get_path_date(self.date_posted)

    @property
    def datetime_posted_path(self):
        return self.get_path_datetime(self.date_posted)

    @property
    def score_display(self):
        return '{:,}'.format(self.score)

    @property
    def extraction_date_display(self):
        return self.get_display_datetime(self.extraction_date)

    @property
    def extraction_date_export(self):
        return self.get_display_datetime(self.extraction_date)

    def set_extracted(self):
        self.extracted = True
        self.extraction_date = datetime.now()
        self.extraction_error = None
        self.error_message = None
        self.get_session().commit()

    def set_extraction_failed(self, error, message):
        self.extracted = False
        self.extraction_date = datetime.now()
        self.extraction_error = error
        self.error_message = message
        self.retry_attempts += 1
        self.get_session().commit()


class Comment(BaseModel):

    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    body = Column(String)
    body_html = Column(String)
    score = Column(Integer)
    date_added = Column(DateTime, default=datetime.now())
    date_posted = Column(DateTime)
    reddit_id = Column(String(collation='NOCASE'), unique=True)

    extracted = Column(Boolean, default=False)
    has_content = Column(Boolean, default=False)
    extraction_date = Column(DateTime, nullable=True)
    extraction_error = Column(Enum(Error), nullable=True)
    error_message = Column(String, nullable=True)
    retry_attempts = Column(Integer, default=0)

    author_id = Column(ForeignKey('user.id'))
    author = relationship('User', foreign_keys=author_id, backref='comments')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', foreign_keys=subreddit_id, backref='comments')
    post_id = Column(ForeignKey('post.id'))
    post = relationship('Post', backref='comments')
    parent_id = Column(ForeignKey('comment.id'), nullable=True)
    parent = relationship('Comment', remote_side=[id], backref='children')
    download_session_id = Column(ForeignKey('download_session.id'))
    download_session = relationship('DownloadSession', backref='comments')  # session where the comment was extracted

    def __str__(self):
        return f'Comment: {self.id}'

    @property
    def date_added_display(self):
        return self.get_display_datetime(self.date_added)

    @property
    def date_added_export(self):
        return self.get_display_datetime(self.date_added)

    @property
    def date_posted_display(self):
        return self.get_display_datetime(self.date_posted)

    @property
    def date_posted_export(self):
        return self.get_display_datetime(self.date_posted)

    @property
    def score_display(self):
        return '{:,}'.format(self.score)

    @property
    def extraction_date_display(self):
        return self.get_display_datetime(self.extraction_date)

    @property
    def extraction_date_export(self):
        return self.get_display_datetime(self.extraction_date)

    @property
    def post_title(self):
        return self.post.title

    @property
    def short_post_title(self):
        return self.post.short_title

    def set_extracted(self):
        self.extracted = True
        self.extraction_date = datetime.now()
        self.extraction_error = None
        self.error_message = None
        self.get_session().commit()

    def set_extraction_failed(self, error,  message):
        self.extracted = False
        self.extraction_date = datetime.now()
        self.extraction_error = error
        self.error_message = message
        self.retry_attempts += 1
        self.get_session().commit()


class Content(BaseModel):

    __tablename__ = 'content'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(collation='NOCASE'))
    download_title = Column(String(collation='NOCASE'), nullable=True)
    extension = Column(String(collation='NOCASE'))
    url = Column(String(collation='NOCASE'))
    directory_path = Column(String(collation='NOCASE'), nullable=True)
    md5_hash = Column(String(collation='NOCASE'), nullable=True)

    downloaded = Column(Boolean, default=False)
    download_date = Column(DateTime, nullable=True)
    download_error = Column(Enum(Error), nullable=True)
    error_message = Column(String, nullable=True)
    retry_attempts = Column(Integer, default=0)

    user_id = Column(ForeignKey('user.id'))
    user = relationship('User', backref='content')
    subreddit_id = Column(ForeignKey('subreddit.id'))
    subreddit = relationship('Subreddit', backref='content')
    post_id = Column(ForeignKey('post.id'), nullable=True)
    post = relationship('Post', backref='content')
    comment_id = Column(ForeignKey('comment.id'), nullable=True)
    comment = relationship('Comment', backref='content')
    download_session_id = Column(ForeignKey('download_session.id'), nullable=True)
    # The session in which this content was actually downloaded.  May differ from the parent post/comment
    # download_session if the content was unable to be downloaded during the same session, and was downloaded at a
    # later date.
    download_session = relationship('DownloadSession', backref='content')

    def __str__(self):
        return f'Content: {self.title}'

    @property
    def short_title(self):
        length = injector.get_settings_manager().short_title_char_length
        if length > 0:
            return self.title[:length]
        else:
            return self.title

    @property
    def download_date_display(self):
        return self.get_display_datetime(self.download_date)

    @property
    def download_date_export(self):
        return self.get_display_datetime(self.download_date)

    @property
    def is_image(self):
        return self.extension in const.IMAGE_EXT

    @property
    def is_gif(self):
        return self.extension in const.GIF_EXT

    @property
    def is_video(self):
        return self.extension in const.VID_EXT

    @property
    def is_animated(self):
        return self.is_gif or self.is_video

    @property
    def is_text(self):
        return self.extension in const.TEXT_EXT

    def get_full_file_path(self, download_title=None):
        if not download_title:
            download_title = self.download_title
        return system_util.join_path(self.directory_path, f'{download_title}.{self.extension}')

    def set_downloaded(self, download_session_id):
        self.download_session_id = download_session_id
        self.downloaded = True
        self.download_date = datetime.now()
        self.download_error = None
        self.error_message = None
        self.get_session().commit()

    def set_download_error(self, error, message):
        self.downloaded = False
        self.download_error = error
        self.error_message = message
        self.retry_attempts = self.retry_attempts + 1
        self.get_session().commit()
