from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as EnumColumn
from uuid import uuid4

from ..database.database_handler import DatabaseHandler
from ..database.models import RedditObjectList


Base = DatabaseHandler.base


class Interval(Enum):

    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    WEEK = 5  # deprecated - do not use

    MONDAY = 6
    TUESDAY = 7
    WEDNESDAY = 8
    THURSDAY = 9
    FRIDAY = 10
    SATURDAY = 11
    SUNDAY = 12

    @property
    def unit(self):
        return self.name.lower()


def generate_uuid():
    return uuid4().hex


class DownloadTask(Base):

    __tablename__ = 'download_task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    interval = Column(EnumColumn(Interval))
    value = Column(String, nullable=True)
    user_list_id = Column(ForeignKey('reddit_object_list.id'), nullable=True)
    user_list = relationship(RedditObjectList, backref='scheduled_user_downloads', foreign_keys=[user_list_id])
    subreddit_list_id = Column(ForeignKey('reddit_object_list.id'), nullable=True)
    subreddit_list = relationship(RedditObjectList, backref='scheduled_subreddit_downloads',
                                  foreign_keys=[subreddit_list_id])
    tag = Column(String, default=generate_uuid, unique=True)
    active = Column(Boolean, default=True)

    @property
    def display(self):
        return f'Every {self.interval} at {self.value}'

    @property
    def user_list_display(self):
        try:
            return self.user_list.name
        except AttributeError:
            return None

    @property
    def subreddit_list_display(self):
        try:
            return self.subreddit_list.name
        except AttributeError:
            return None
