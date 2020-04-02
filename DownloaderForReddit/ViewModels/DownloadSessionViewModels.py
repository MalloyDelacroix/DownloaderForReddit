import logging
from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QAbstractItemModel, Qt, QSize, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon


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

    def __init__(self):
        super().__init__()
        self.sessions = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.sessions)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.sessions[index.row()].name
        elif role == Qt.ToolTipRole:
            session = self.sessions[index.row()]
            return f'Start time: {session.start_time_display}\n' \
                   f'End time: {session.end_time_display}\n' \
                   f'Duration: {session.duration}\n' \
                   f'Reddit Objects: {session.get_downloaded_reddit_object_count()}\n' \
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

    def set_data(self, data):
        self.posts.clear()
        self.beginInsertRows(QModelIndex(), 0, len(data))
        self.posts = data
        self.endInsertRows()

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
            return self.get_post_attribute(index.column(), self.posts[index.row()])
        if role == Qt.ToolTipRole:
            if index.column() == 0:
                return self.posts[index.row()].title
            elif index.column() == 4:
                return self.posts[index.row()].text
        return None

    def get_post_attribute(self, column, post):
        attrs = {
            0: post.title,
            1: post.date_posted_display,
            2: post.score_display,
            3: post.nsfw,
            4: post.text,
            5: post.author.name,
            6: post.subreddit.name
        }
        return attrs[column]

    def refresh(self):
        first = self.createIndex(0, 0)
        second = self.createIndex(self.columnCount(), self.rowCount())
        self.dataChanged.emit(first, second)


class ContentListView(QAbstractListModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.content_list = []
        self.pixmap_map = {}

    def set_data(self, data):
        self.pixmap_map.clear()
        self.content_list.clear()
        self.beginInsertRows(QModelIndex(), 0, len(data) - 1)
        self.content_list = data
        self.endInsertRows()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.content_list)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.content_list[index.row()].title
        elif role == Qt.DecorationRole:
            icon = self.get_icon(self.content_list[index.row()])
            return icon
        elif role == Qt.ToolTipRole:
            return self.content_list[index.row()].title
        return None

    def get_icon(self, content):
        try:
            pixmap = self.pixmap_map[content.id]
        except KeyError:
            pixmap = QPixmap(content.full_file_path).scaled(QSize(500, 500), Qt.KeepAspectRatio)
            self.pixmap_map[content.id] = pixmap
        return QIcon(pixmap)
