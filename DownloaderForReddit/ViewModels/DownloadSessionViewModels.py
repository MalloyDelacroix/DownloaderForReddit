import logging
from sqlalchemy.orm import joinedload
from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QAbstractItemModel, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

from ..Database.Models import DownloadSession, RedditObject, Post, Content, Comment
from ..Utils import Injector


class CustomItemModel:

    def refresh(self):
        """
        Refreshes the displayed items in the list. This has to be called when the sort order is changed or the new
        sort order will not be displayed until the list is moved.
        """
        first = self.createIndex(0, 0)
        second = self.createIndex(0, self.rowCount())
        self.dataChanged.emit(first, second)


class DownloadSessionModel(QAbstractListModel, CustomItemModel):

    def __init__(self, download_session=None):
        super().__init__()
        self.db = Injector.get_database_handler()
        self.current_session = download_session or self.get_last_session()
        self.sessions = self.get_sessions()

    def get_last_session(self):
        with self.db.get_scoped_session() as session:
            return session.query(DownloadSession).first()

    def get_sessions(self):
        with self.db.get_scoped_session() as session:
            return session.query(DownloadSession).options(joinedload('posts'), joinedload('content')).all()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.sessions)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.sessions[index.row()].name
        elif role == Qt.ToolTipRole:
            session = self.sessions[index.row()]
            with self.db.get_scoped_session() as db_session:
                return f'Start time: {session.start_time}\n' \
                       f'End time: {session.end_time}\n' \
                       f'Duration: {session.duration}\n' \
                       f'Reddit Objects: {session.get_downloaded_reddit_object_count(db_session)}\n' \
                       f'Posts: {len(session.posts)}\n' \
                       f'Content: {len(session.content)}'
        return None


class RedditObjectModel(QAbstractListModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.reddit_object_list = []

    def set_data(self, data):
        self.reddit_object_list = data
        self.refresh()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.reddit_object_list)

    def data(self, index, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.reddit_object_list[index.row()].name
        return None


class PostTableModel(QAbstractTableModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.posts = []
        self.headers = ['title', 'date_posted', 'score', 'nsfw', 'text', 'author', 'subreddit']

    def headerData(self, row, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[row].replace('_', ' ').title()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.posts)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.headers)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return getattr(self.posts[index.row()], self.headers[index.column()])


class ContentListView(QAbstractListModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.content_list = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.content_list)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.content_list[index.row()].name
        elif role == Qt.DecorationRole:
            content = self.content_list[index.row()]
            pixmap = QPixmap(content.full_file_path).scaled(QSize(500, 500), Qt.KeepAspectRatio)
            return QIcon(pixmap)
