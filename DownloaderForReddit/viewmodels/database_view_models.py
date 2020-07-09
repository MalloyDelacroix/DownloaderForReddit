from PyQt5.QtCore import (QAbstractListModel, QAbstractTableModel, QAbstractItemModel, Qt, QSize, QModelIndex, QVariant,
                          pyqtSignal)
from PyQt5.QtGui import QPixmap, QIcon

from ..utils import injector


class CustomItemModel:

    update_count = pyqtSignal(tuple)

    settings_manager = injector.get_settings_manager()
    db = injector.get_database_handler()

    def __init__(self):
        super().__init__()
        self.limit = 50
        self.headers = []
        self.items = []
        self.total_items = 0
        self.loading = False
        self.last_count = 0

    @property
    def has_next_page(self):
        return len(self.items) < self.total_items

    def contains(self, item):
        return item in self.items

    def get_item(self, row):
        if row >= 0:
            return self.items[row]
        else:
            raise IndexError

    def get_items(self, indices):
        items = []
        rows = set(x.row() for x in indices)
        for x in rows:
            items.append(self.items[x])
        return items

    def get_item_index(self, item):
        try:
            return self.createIndex(self.items.index(item), 0)
        except ValueError:
            return self.createIndex(0, 0)

    def get_item_index_by_id(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return self.get_item_index(item)
        return self.createIndex(0, 0)

    def set_data(self, query):
        self.total_items = query.count()
        data = query.limit(self.limit).all()
        self.beginRemoveRows(QModelIndex(), 0, len(self.items))
        self.items.clear()
        self.endRemoveRows()
        self.beginInsertRows(QModelIndex(), 0, len(data))
        self.items = data
        self.endInsertRows()

    def load_next_page(self, query):
        if self.has_next_page and not self.loading:
            self.loading = True
            data = query.offset(len(self.items)).limit(self.limit).all()
            self.beginInsertRows(QModelIndex(), 0, len(data))
            self.items.extend(data)
            self.endInsertRows()
            self.loading = False

    def rowCount(self, parent=None, *args, **kwargs):
        row_count = len(self.items)
        if row_count != self.last_count:
            self.update_count.emit((row_count, self.total_items))
            self.last_count = row_count
        return row_count

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.headers)

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
        self.limit = self.settings_manager.download_session_query_limit

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.items[index.row()].name
        elif role == Qt.ToolTipRole:
            session = self.items[index.row()]
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
        self.limit = self.settings_manager.reddit_object_query_limit

    def data(self, index, role=None):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.items[index.row()].name
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
        'nsfw': lambda x: x.nsfw,
        'extracted': lambda x: x.extracted,
        'extraction_date': lambda x: x.extraction_date,
        'extraction_error': lambda x: x.extraction_error,
    }

    def __init__(self):
        super().__init__()
        self.limit = self.settings_manager.post_query_limit
        self.headers = ['title', 'date_posted', 'score', 'self_post', 'text', 'url', 'domain', 'author',
                        'subreddit', 'nsfw', 'extracted', 'extraction_date', 'extraction_error']

    def headerData(self, row, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[row].replace('_', ' ').title()

    def data(self, index, role=None):
        col = index.column()
        if role == Qt.DisplayRole:
            return self.header_map[self.headers[col]](self.items[index.row()])
        if role == Qt.ToolTipRole:
            if col != self.headers.index('text'):
                return self.header_map[self.headers[col]](self.items[index.row()])
        return None

    def get_post_attribute(self, column, post):
        attr = self.headers[column]
        value = getattr(post, attr)
        if attr == 'subreddit' or attr == 'author':
            return value.name
        return value


class ContentListModel(QAbstractListModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.limit = self.settings_manager.content_query_limit
        self.icon_map = {}

    def set_data(self, query):
        self.icon_map.clear()
        super().set_data(query)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.items[index.row()].title
        elif role == Qt.DecorationRole:
            icon = self.get_icon(self.items[index.row()])
            return icon
        elif role == Qt.ToolTipRole:
            return self.items[index.row()].title
        return None

    def get_icon(self, content):
        """
        Checks the icon map for an icon that matches the supplied content's id.  If one is not found, an icon is created
        from the file at the contents file path and the icon is stored in the icon map before being returned.  This is
        done so that new pixmaps do not have to be created for the content everytime the 'data' method is called.
        :param content: The content for which an icon is requested.
        :return: An icon to be displayed.
        """
        try:
            icon = self.icon_map[content.id]
        except KeyError:
            pixmap = QPixmap(content.get_full_file_path()).scaled(QSize(500, 500), Qt.KeepAspectRatio)
            icon = QIcon()
            icon.addPixmap(pixmap, QIcon.Normal)
            icon.addPixmap(pixmap, QIcon.Selected)
            self.icon_map[content.id] = icon
        return icon


class CommentTreeModel(QAbstractItemModel, CustomItemModel):

    def __init__(self):
        super().__init__()
        self.limit = self.settings_manager.comment_query_limit
        self.headers = ['author', 'id', 'subreddit', 'body', 'body_html', 'score', 'date_posted', 'reddit_id']
        self.root = TreeItem(None, None)

    def contains(self, item):
        return self.cascade_contains(self.items, item)

    def cascade_contains(self, searchable, item):
        for x in searchable:
            if x == item:
                return True
            else:
                return self.cascade_contains(x.children, item)
        return False

    def get_first_index(self):
        try:
            return self.index(0, 0, QModelIndex())
        except IndexError:
            return self.createIndex(0, 0)

    def get_item_index(self, item):
        return self.cascade_get_item_index(self.root, item)

    def cascade_get_item_index(self, searchable, item):
        for x in searchable.children:
            if x.data(0, Qt.UserRole) == item:
                return self.createIndex(x.row(), 0, searchable)
            else:
                return self.cascade_get_item_index(x, item)

    def get_item(self, index):
        try:
            return index.internalPointer().data(0, Qt.UserRole)
        except AttributeError:
            return None

    def get_items(self, indices):
        try:
            return [index.internalPointer().data(0, Qt.UserRole) for index in indices]
        except AttributeError:
            return None

    def set_data(self, query):
        self.total_items = query.count()
        data = query.limit(self.limit).all()
        self.beginRemoveRows(QModelIndex(), 0, len(self.items))
        self.items.clear()
        self.root = TreeItem(None, None)
        self.endRemoveRows()
        self.beginInsertRows(QModelIndex(), 0, len(data))
        self.items = data
        for comment in self.items:
            self.add_tree_item(comment, self.root)
        self.endInsertRows()

    def load_next_page(self, query):
        if self.has_next_page and not self.loading:
            self.loading = True
            data = query.offset(len(self.items)).limit(self.limit).all()
            self.beginInsertRows(QModelIndex(), 0, len(data))
            self.items.extend(data)
            for comment in data:
                self.add_tree_item(comment, self.root)
            self.endInsertRows()

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
        if role == Qt.DisplayRole or role == Qt.ToolTipRole or role == Qt.UserRole:
            return item.data(index.column(), role)
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
            row_count = 0
        else:
            if not parent.isValid():
                item = self.root
            else:
                item = parent.internalPointer()
            row_count = item.childCount()
        self.update_count.emit((row_count, self.total_items))
        return row_count


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
        elif role == Qt.UserRole:
            return self.comment
        return QVariant(self.headers[column])

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0
