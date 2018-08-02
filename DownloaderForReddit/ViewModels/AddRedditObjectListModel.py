"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
from queue import Queue

from Utils.RedditUtils import NameChecker


class AddRedditObjectListModel(QAbstractListModel):
    """
    A list model that handles the the list view for the AddRedditObjectDialog.
    """

    name_list_updated = pyqtSignal()

    def __init__(self, object_type, parent=None):
        super().__init__()
        self.parent = parent
        self.object_type = object_type
        self.queue = Queue()
        self.name_list = []
        self.validation_dict = {}

        self.name_checker = None
        self.start_name_check_thread()
        self.checker_running = True

        valid_path = os.path.abspath('Resources/Images/valid_checkmark.png')
        non_valid_path = os.path.abspath('Resources/Images/non_valid_x.png')
        self.valid_img = QPixmap(valid_path)
        self.non_valid_img = QPixmap(non_valid_path)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.name_list)

    def insertRow(self, name, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.name_list.append(name)
        self.validation_dict[name] = None
        self.queue.put(name)
        self.name_list_updated.emit()
        self.endInsertRows()
        return True

    def removeRows(self, pos, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, pos, pos + rows - 1)
        for x in range(rows):
            name = self.name_list[pos]
            self.name_list.remove(name)
            del self.validation_dict[name]
        self.name_list_updated.emit()
        self.endRemoveRows()
        return True

    def clear_non_valid(self):
        """Removes all non-valid names from the name list."""
        name_list = []
        for key, value in self.validation_dict.items():
            if not value:
                name_list.append(key)
        for name in name_list:
            self.removeRows(self.name_list.index(name), 1)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.name_list[index.row()]
        elif role == Qt.DecorationRole:
            name = self.name_list[index.row()]
            if self.validation_dict[name] is None:
                return None
            if self.validation_dict[name]:
                return self.valid_img
            else:
                return self.non_valid_img

    def start_name_check_thread(self):
        """Initializes a NameChecker object, then runs it in another thread."""
        self.name_checker = NameChecker(self.object_type, self.queue)
        self.thread = QThread(self)
        self.name_checker.moveToThread(self.thread)
        self.name_checker.name_validation.connect(self.validate_name)
        self.name_checker.finished.connect(self.thread.quit)
        self.name_checker.finished.connect(self.name_checker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.name_checker.run)
        self.thread.start()

    def stop_name_checker(self):
        if self.name_checker:
            self.name_checker.stop_run()

    def validate_name(self, name_tup):
        self.validation_dict[name_tup[0]] = name_tup[1]
        index = self.createIndex(self.name_list.index(name_tup[0]), 0)
        self.dataChanged.emit(index, index)
