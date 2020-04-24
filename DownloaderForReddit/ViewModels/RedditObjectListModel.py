import logging
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QColor
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from ..Core.RedditObjectCreator import RedditObjectCreator
from ..Utils import Injector
from ..Database.Models import RedditObject, RedditObjectList


class RedditObjectListModel(QAbstractListModel):

    reddit_object_added = pyqtSignal(int)

    def __init__(self, list_type):
        """
        A list model that holds a list of reddit objects to display.  Handles calls to the database made through the
        GUI.
        """
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()
        self.list_type = list_type
        self.list = None
        self.reddit_objects = None
        self.row_count = 0

        self.validator = None
        self.validation_thread = None
        self.validating = False

        # TODO: add waiting overlay to list while waiting on objects to validate

    def get_id_list(self):
        return [x.id for x in self.reddit_objects]

    def get_object(self, object_name):
        for ro in self.reddit_objects:
            if ro.name == object_name:
                return ro
        return None

    def add_new_list(self, list_name, list_type):
        creator = RedditObjectCreator(list_type)
        ro_list = creator.create_reddit_object_list(list_name)
        if ro_list is not None:
            self.list = ro_list
            self.reddit_objects = self.list.reddit_objects
            self.row_count = self.list.reddit_objects.count()
            return True
        return False

    def delete_current_list(self):
        # TODO: delete list and commit
        pass

    def set_list(self, list_name):
        try:
            self.list = self.session.query(RedditObjectList)\
                .filter(RedditObjectList.name == list_name)\
                .filter(RedditObjectList.list_type == self.list_type)\
                .one()
            self.reddit_objects = self.list.reddit_objects
            self.row_count = self.list.reddit_objects.count()
            self.refresh()
            # TODO: sort list here
        except NoResultFound:
            pass

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
        ro = self.session.query(RedditObject).filter(func.lower(RedditObject.name) == func.lower(name)).scalar()
        return ro in self.reddit_objects

    def delete_reddit_object(self, reddit_object):
        self.list.reddit_objects.remove(reddit_object)
        self.session.commit()
        # TODO: decide whether or not to delete the reddit object completely, or leave it in the database but removed
        #       from the list

    def add_reddit_object(self, name: str):
        self.add_reddit_objects([name])

    def add_reddit_objects(self, name_list: list):
        """
        A long and complicated method so that name validation can be done in a separate thread.  Sqllite objects can't
        be modified from a different thread than the one that they were created in.  This necessitates using PyQt's
        threading frame work, which is much more verbose than Python's standard, but which does support signaling.
        :param name_list: A list of names to be validated, made into reddit objects, and added to the current reddit
                          object list.
        """
        self.validating = True
        self.validation_thread = QThread()
        self.validator = ObjectValidator(name_list, self.list_type, list_defaults=self.list.get_default_dict())
        self.validation_thread.started.connect(self.validator.run)
        self.validator.new_object_signal.connect(self.add_validated_reddit_object)
        self.validator.invalid_name_signal.connect(lambda name: print(f'Invalid name: {name}'))
        self.validator.finished.connect(self.validation_thread.quit)
        self.validation_thread.finished.connect(self.validator.deleteLater)
        self.validation_thread.finished.connect(self.validation_thread.deleteLater)
        self.validator.moveToThread(self.validation_thread)
        self.validation_thread.start()

    def add_validated_reddit_object(self, ro_id):
        reddit_object = self.session.query(RedditObject).get(ro_id)
        self.insertRow(reddit_object)

    def insertRow(self, item, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.list.reddit_objects.append(item)
        self.endInsertRows()
        self.session.commit()
        self.reddit_object_added.emit(item.id)
        self.row_count += 1
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, position, position - 1)
        for x in range(rows):
            self.list.reddit_objects.remove(self.list.reddit_objects[position])
        self.endRemoveRows()
        self.session.commit()
        self.row_count -= 1
        return True

    def removeRow(self, row, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, row, row)
        del self.list.reddit_objects[row]
        self.endRemoveRows()
        self.session.commit()
        return True

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        try:
            return self.row_count
        except AttributeError:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        try:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.reddit_objects[row].name
            elif role == Qt.ForegroundRole:
                if not self.reddit_objects[row].download_enabled:
                    return QColor(255, 0, 0, 255)  # set name text to red if download is disabled
                else:
                    return None
            elif role == Qt.ToolTipRole:
                return self.set_tooltips(self.reddit_objects[row])
            elif role == Qt.UserRole:
                return self.reddit_objects[row]
            else:
                return None
        except IndexError:
            pass

    def raw_data(self, row):
        try:
            return self.reddit_objects[row]
        except IndexError:
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
            'download_naming_method': f'Name Downloads By: {reddit_object.post_download_naming_method}',
            'subreddit_save_method': f'Subreddit Save Method: {reddit_object.post_save_structure}',
            'download_images': f'Download Images: {reddit_object.download_images}',
            'download_videos': f'Download Videos: {reddit_object.download_videos}',
            'download_nsfw': f'NSFW Filter: {reddit_object.download_nsfw.display_name}',
            'date_added': f'Date Added: {reddit_object.date_added}'
        }
        tooltip = ''
        for key, value in tooltip_dict.items():
            if self.settings_manager.main_window_tooltip_display_dict[key]:
                tooltip += '%s\n' % value
        return tooltip.strip()

    def nsfw_filter_display(self, filter_method):
        for key, value in self.settings_manager.nsfw_filter_dict.items():
            if value == filter_method:
                return key

    def flags(self, QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def refresh(self):
        """
        Refreshes the displayed items in the list. This has to be called when the sort order is changed or the new
        sort order will not be displayed until the list is moved.
        """
        first = self.createIndex(0, 0)
        second = self.createIndex(0, self.rowCount())
        self.dataChanged.emit(first, second)


class ObjectValidator(QObject):

    new_object_signal = pyqtSignal(int)
    invalid_name_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, name_list, list_type, list_defaults):
        super().__init__()
        self.name_list = name_list
        self.list_type = list_type
        self.list_defaults = list_defaults

    def run(self):
        object_creator = RedditObjectCreator(self.list_type)
        for name in self.name_list:
            reddit_object_id = object_creator.create_reddit_object(name, self.list_defaults)
            if reddit_object_id is not None:
                self.new_object_signal.emit(reddit_object_id)
            else:
                self.invalid_name_signal.emit(name)
        self.finished.emit()
