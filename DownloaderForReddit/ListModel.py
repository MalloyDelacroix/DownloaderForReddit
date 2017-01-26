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


from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
from operator import attrgetter


class ListModel(QAbstractListModel):

    def __init__(self, name, list_type):
        """
        A model of reddit objects (users or subreddits) to be displayed in the GUI list views

        :param name: The name of the list
        :param list_type: The type of list (user or subreddit)

        The reddit_object_list is a list of actual objects which are instances of the RedditObjects subclasses
        The display_list is a list of the names of the items in the reddit_object_list as strings. These are what
        are actually displayed in the list view
        """
        super().__init__()
        self.name = name
        self.list_type = list_type
        self.reddit_object_list = []
        self.display_list = [x.name for x in self.reddit_object_list]

    def sort_lists(self, method):
        """Sorts the lists according to the method set in the settings dialog"""
        if method[0] == 0:
            att_method = 'name'
        elif method[0] == 1:
            att_method = 'user_added'
        else:
            att_method = 'number_of_downloads'

        self.reddit_object_list = sorted(self.reddit_object_list, key=attrgetter(att_method), reverse=method[1])
        self.display_list = [x.name for x in self.reddit_object_list]

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        for x in range(rows):
            new_name = "New User %s" % self.rowCount()
            self.display_list.append(new_name)
            self.reddit_object_list.insert(position, new_name)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for x in range(rows):
            self.display_list.remove(self.reddit_object_list[position].name)
            self.reddit_object_list.remove(self.reddit_object_list[position])
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.reddit_object_list)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.display_list[index.row()]
        elif role == Qt.DecorationRole:
            return None
        elif role == Qt.ToolTipRole:
            return None
        elif role == Qt.EditRole:
            return self.display_list[index.row()]

    def flags(self, QModelIndex):
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            obj = self.reddit_object_list[index]
            if value in self.display_list:
                return False
            else:
                self.reddit_object_list[index] = value
                self.display_list.remove(obj)
                self.display_list.append(value.name)
