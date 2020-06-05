from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import Enum as EnumColumn
from uuid import uuid4

from ..database.database_handler import DatabaseHandler


Base = DatabaseHandler.base


class Interval(Enum):

    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    WEEK = 5

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


class DownloadTask(Base):

    __tablename__ = 'download_task'

    id = Column(Integer, primary_key=True, autoincrement=True)
    interval = Column(EnumColumn(Interval))
    value = Column(String, nullable=True)
    user_list_id = Column(Integer, nullable=True)
    subreddit_list_id = Column(Integer, nullable=True)
    tag = Column(String, default=uuid4().hex, unique=True)
    active = Column(Boolean, default=True)
