import logging
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt5.QtGui import QColor
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from ..Utils import Injector
from ..Database.Models import RedditObject, RedditObjectList


class RedditObjectListModel(QAbstractListModel):

    def __init__(self):
        """
        A list model that holds a list of reddit objects to display.  Handles calls to the database made through the
        GUI.
        """
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()
        self.list = None
        self.reddit_objects = None

    def commit_changes(self):
        self.session.commit()

    def add_new_list(self, list_name, list_type):
        new_list = RedditObjectList(name=list_name, list_type=list_type)
        self.session.add(new_list)
        self.session.commit()
        self.list = new_list

    def delete_current_list(self):
        pass

    def set_list(self, list_name):
        try:
            self.list = self.session.query(RedditObjectList).filter(RedditObjectList.name == list_name).one()
            self.reddit_objects = self.list.reddit_objects
            # TODO: sort list here
        except NoResultFound:
            print('No reddit object list found')
            pass  # TODO: to log or not to log...

    def sort_list(self, method, order):
        try:
            # TODO: map this to user selectable sort methods
            self.reddit_objects = self.list.reddit_objects.order_by(RedditObject.name)
        except AttributeError:
            pass

    def check_name(self, name):
        """
        Checks the reddit object list to see if an object with the supplied name exists in the list.
        :param name: The name that is to be checked for existence.
        :return: True if the name exists, False if it does not.
        :type name: str
        :rtype: bool
        """
        return self.session.query(RedditObject).filter(RedditObject.name == name).scalar() is not None

    def delete_reddit_object(self, reddit_object):
        self.list.reddit_objects.remove(reddit_object)

    def add_reddit_object(self, reddit_object):
        self.insertRow(reddit_object)

    def insertRow(self, item, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.list.reddit_objects.append(item)
        self.endInsertRows()
        self.session.commit()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, position, position - 1)
        for x in range(rows):
            self.list.reddit_objects.remove(self.list.reddit_objects[position])
        self.endRemoveRows()
        self.session.commit()
        return True

    def removeRow(self, row, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, row, row)
        del self.list.reddit_objects[row]
        self.endRemoveRows()
        self.session.commit()
        return True

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        try:
            return self.list.reddit_objects.count()
        except AttributeError:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.reddit_objects[row].name
        elif role == Qt.ForegroundRole:
            if not self.reddit_objects[row].download_enabled:
                return QColor(255, 0, 0, 255)  # set name text to red if download is disabled
            else:
                return None
        elif role == Qt.ToolTipRole:
            return self.set_tooltips(self.reddit_objects[row])
        else:
            return None

    def set_tooltips(self, reddit_object):
        """
        Builds the tooltip text based on what options are selected in the settings manager and returns the text.
        :param reddit_object: The reddit object the tooltip text is based off of.
        :type reddit_object: RedditObject
        :return: Text formatted to be displayed as a tooltip.
        :rtype: str
        """
        tooltip_dict = {
            'name': f'Name: {reddit_object.name}',
            'download_enabled': f'Download Enabled: {reddit_object.download_enabled}',
            'lock_settings': f'Settings Locked: {reddit_object.lock_settings}',
            'last_download_date': f'Last Download: {reddit_object.last_download}',
            'date_limit': f'Date Limit: {reddit_object.date_limit}',
            'absolute_date_limit': f'Absolute Date Limit: {reddit_object.absolute_date_limit}',
            'post_limit': f'Post Limit: {reddit_object.post_limit}',
            'download_naming_method': f'Name Downloads By: {reddit_object.download_naming_method}',
            'subreddit_save_method': f'Subreddit Save Method: {reddit_object.subreddit_save_structure}',
            'download_images': f'Download Images: {reddit_object.download_images}',
            'download_videos': f'Download Videos: {reddit_object.download_videos}',
            'avoid_duplicates': f'Avoid Duplicates: {reddit_object.avoid_duplicates}',
            'nsfw_filter': f'NSFW Filter: {self.nsfw_filter_display(reddit_object.download_nsfw)}',
            'undownloaded_content_count': f'Undownloaded Content: {"TODO: add undownloaded count"}',
            'unextracted_post_count': f'Unextracted Posts: {"TODO: add unextracted count"}',
            'total_downloads': f'Total Downloads: {"TODO: add total download count"}',
            'date_added': f'Date Added: {reddit_object.date_added}'
        }
        tooltip = ''
        for key, value in tooltip_dict.items():
            if self.settings_manager.tooltip_display_dict[key]:
                tooltip += '%s\n' % value
        return tooltip.strip()

    def nsfw_filter_display(self, filter_method):
        for key, value in self.settings_manager.nsfw_filter_dict.items():
            if value == filter_method:
                return key

    def flags(self, QModelIndex):
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def refresh(self):
        """
        Refreshes the displayed items in the list. This has to be called when the sort order is changed or the new
        sort order will not be displayed until the list is moved.
        """
        first = self.createIndex(0, 0)
        second = self.createIndex(0, self.rowCount())
        self.dataChanged.emit(first, second)

