import logging
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QColor
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from ..core.reddit_object_creator import RedditObjectCreator
from ..utils import injector
from ..database.models import RedditObject, RedditObjectList
from ..database.filters import RedditObjectFilter


class RedditObjectListModel(QAbstractListModel):

    starting_add = pyqtSignal(object)
    finished_add = pyqtSignal()
    reddit_object_added = pyqtSignal(int)
    existing_object_added = pyqtSignal(tuple)

    def __init__(self, list_type):
        """
        A list model that holds a list of reddit objects to display.  Handles calls to the database made through the
        GUI.
        """
        super().__init__()
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
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
            self.session.add(ro_list)
            self.list = ro_list
            self.reddit_objects = self.list.reddit_objects.all()
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
            self.row_count = self.list.reddit_objects.count()
            self.sort_list()
        except NoResultFound:
            pass

    def sort_list(self):
        try:
            order = self.settings_manager.list_order_method
            desc = self.settings_manager.order_list_desc
            f = RedditObjectFilter()
            self.reddit_objects = f.filter(self.session, query=self.list.reddit_objects, order_by=order, desc=desc).all()
            self.refresh()
        except AttributeError:
            # AttributeError indicates that no list is set for this view model
            pass

    def search_list(self, term):
        f = RedditObjectFilter()
        if term is not None and term != '':
            self.reddit_objects = f.filter(self.session, ('name', 'wild_like', term), query=self.list.reddit_objects,
                                           order_by=self.settings_manager.list_order_method,
                                           desc=self.settings_manager.list_order_method).all()
        else:
            self.reddit_objects = f.filter(self.session, query=self.list.reddit_objects,
                                           order_by=self.settings_manager.list_order_method,
                                           desc=self.settings_manager.list_order_method).all()
        self.refresh()

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
        self.starting_add.emit(self)
        name_list = self.check_existing(name_list)
        self.validating = True
        self.validation_thread = QThread()
        self.validator = ObjectValidator(name_list, self.list_type, list_defaults=self.list.get_default_dict())
        self.validator.moveToThread(self.validation_thread)
        self.validation_thread.started.connect(self.validator.run)
        self.validator.new_object_signal.connect(self.add_validated_reddit_object)
        self.validator.invalid_name_signal.connect(lambda name: print(f'Invalid name: {name}'))
        self.validator.finished.connect(self.validation_thread.quit)
        self.validator.finished.connect(self.validator.deleteLater)
        self.validator.finished.connect(self.finish_adding)
        self.validation_thread.finished.connect(self.validation_thread.deleteLater)
        self.validation_thread.start()

    def check_existing(self, name_list):
        """
        Checks the supplied list of names for names that already exist in the database.  If duplicate names are found,
        the existing_object_added signal is emitted and the names are removed from the list.
        :param name_list: A list of names that are to be checked for duplication in the database.
        :return: The supplied list of names with any duplicate names removed.
        """
        existing_ids = []
        existing_names = []
        for name in name_list:
            ro = self.session.query(RedditObject).filter(func.lower(RedditObject.name) == name.lower()).first()
            if ro is not None:
                existing_ids.append(ro.id)
                existing_names.append(ro.name)
                if ro in self.list.reddit_objects:
                    name_list.remove(name)
        if len(existing_names) > 0:
            self.existing_object_added.emit((self.list_type, existing_ids, existing_names))
        return name_list

    def add_validated_reddit_object(self, ro_id):
        reddit_object = self.session.query(RedditObject).get(ro_id)
        self.insertRow(reddit_object)
        self.reddit_objects = self.list.reddit_objects.all()

    def finish_adding(self):
        self.finished_add.emit()

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
        if index.isValid():
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
