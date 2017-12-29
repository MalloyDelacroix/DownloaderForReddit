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


class UserFinderListModel(QAbstractListModel):

    def __init__(self):
        """
        A list model for user finder users to be displayed with access to needed attributes as well as a list of
        user finder extracted links.
        """
        super().__init__()

        self.user_list = []

    def sort_lists(self, method):
        """
        Sorts the user list based on the supplied method tuple.
        :param method: A tuple, the first item being the method to sort by and the second being ascending or descending
        :type method: tuple
        """
        if method[0] == 'NAME':
            att_method = lambda x: getattr(x, 'name').lower()
        elif method[0] == 'KARMA':
            att_method = attrgetter('total_karma')
        else:
            att_method = attrgetter('last_post_date')
        self.user_list.sort(key=att_method, reverse=method[1])

    def check_name(self, name):
        """Checks the user list to see if the supplied name exists in the list, returns True if it does False if not."""
        pass

    def insertRow(self, item, parent=QModelIndex(), *args):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.user_list.append(item)
        self.endInsertRows()
        return True

    def removeRows(self, row_list, parent=QModelIndex(), *args):
        for x in sorted(row_list, reverse=True):
            self.removeRow(x)

    def removeRow(self, row, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, row, row)
        del self.user_list[row]
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex, *args, **kwargs):
        return len(self.user_list)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.user_list[index].name
        elif role == Qt.DecorationRole:
            return None

    def flags(self, QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled













