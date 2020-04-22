from PyQt5.QtCore import QAbstractListModel, QAbstractTableModel, QAbstractItemModel, Qt, QSize, QModelIndex, QVariant
from PyQt5.QtGui import QPixmap, QIcon

from ..Utils import Injector


class CustomItemModel:

    settings_manager = Injector.get_settings_manager()

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

    def get_item(self, row):
        return self.sessions[row]

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

    def get_item(self, row):
        return self.reddit_object_list[row]

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

    header_map = {
        'title': lambda x: x.title,
        'date_posted': lambda x: x.date_posted_display,
        'score': lambda x: x.score_display,
        'self_post': lambda x: x.is_self,
        'text': lambda x: x.text,
        'url': lambda x: x.url,
        'domain': lambda x: x.domain,
        'author': lambda x: x.author.name,
        'subreddit': lambda x: x.subreddit.name,
        'nsfw': lambda x: x.nsfw
    }

    def __init__(self):
        super().__init__()
        self.posts = []
        self.headers = ['title', 'date_posted', 'score', 'self_post', 'text', 'url', 'domain', 'author',
                        'subreddit', 'nsfw']

    def get_item(self, row):
        return self.posts[row]

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
        col = index.column()
        if role == Qt.DisplayRole:
            return self.header_map[self.headers[col]](self.posts[index.row()])
        if role == Qt.ToolTipRole:
            if col != self.headers.index('text'):
                return self.header_map[self.headers[col]](self.posts[index.row()])
        return None

    def get_post_attribute(self, column, post):
        attr = self.headers[column]
        value = getattr(post, attr)
        if attr == 'subreddit' or attr == 'author':
            return value.name
        return value

    def refresh(self):
        first = self.createIndex(0, 0)
        second = self.createIndex(self.columnCount(), self.rowCount())
        self.dataChanged.emit(first, second)


class ContentListModel(QAbstractListModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.content_list = []
        self.pixmap_map = {}

    def get_item(self, row):
        return self.content_list[row]

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
            pixmap = QPixmap(content.get_full_file_path()).scaled(QSize(500, 500), Qt.KeepAspectRatio)
            self.pixmap_map[content.id] = pixmap
        return QIcon(pixmap)


class CommentTreeModel(QAbstractItemModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.headers = ['author', 'id', 'subreddit', 'body', 'body_html', 'score', 'date_posted', 'reddit_id']
        self.top_level_comments = []
        self.root = TreeItem(None, None)

    def set_data(self, top_level_comments):
        self.top_level_comments.clear()
        self.root.clear()
        self.top_level_comments = top_level_comments
        for comment in top_level_comments:
            self.add_tree_item(comment, self.root)

    def add_tree_item(self, comment, parent):
        item = TreeItem(comment, parent)
        parent.appendChild(item)
        for child in comment.children:
            self.add_tree_item(child, item)

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(self.headers)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return item.data(index.column(), role)
        elif role == Qt.UserRole:
            if item:
                return item.comment
        return QVariant()

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.headers[column]
            except IndexError:
                pass
        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent = self.root
        else:
            parent = parent.internalPointer()
        child = parent.child(row)
        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child = index.internalPointer()
        if not child:
            return QModelIndex()
        parent = child.parent
        if parent == self.root:
            return QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent=None):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            item = self.root
        else:
            item = parent.internalPointer()
        return item.childCount()


class TreeItem:

    header_map = {
        'author': lambda x: x.author.name,
        'id': lambda x: x.id,
        'subreddit': lambda x: x.subreddit.name,
        'body': lambda x: x.body,
        'body_html': lambda x: x.body_html,
        'score': lambda x: x.score,
        'date_posted': lambda x: x.date_posted_display,
        'reddit_id': lambda x: x.reddit_id,
    }

    def __init__(self, comment, parent):
        self.comment = comment
        self.parent = parent
        self.children = []
        self.headers = ['author', 'id', 'subreddit', 'body', 'body_html', 'score', 'date_posted', 'reddit_id']

    def clear(self):
        for child in self.children:
            child.clear()
        self.children.clear()

    def appendChild(self, item):
        self.children.append(item)

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.headers)

    def data(self, column, role):
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            header = self.headers[column]
            return self.header_map[header](self.comment)
        return QVariant(self.headers[column])

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0
