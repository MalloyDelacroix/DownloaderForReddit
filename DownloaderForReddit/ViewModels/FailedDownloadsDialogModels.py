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

from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant


class FailedDownloadsTableModel(QAbstractTableModel):

    def __init__(self, failed_list):
        super().__init__()
        self.data_list = failed_list
        self.header_data = ['Author', 'Subreddit', 'Title', 'Date Posted', 'Url', 'Status', 'Save Status']

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data_list)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.header_data)

    def headerData(self, col, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return QVariant(self.header_data[col])
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole and role != Qt.ToolTipRole:
            return None
        row = index.row()
        col = index.column()
        try:
            item = getattr(self.data_list[row], attrify(self.header_data[col]))
        except AttributeError:
            item = None
        return item


class FailedDownloadsDetailTableModel(QAbstractTableModel):

    def __init__(self, post):
        super().__init__()
        self.post = post
        self.index_dict = {0: 'Author', 1: 'Subreddit', 2: 'Title', 3: 'Date Posted', 4: 'Url', 5: 'Status',
                           6: 'Save Status'}

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def rowCount(self, parent=None, *args, **kwargs):
        return 7

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid or role != Qt.DisplayRole:
            return None
        attr = self.index_dict[index.row()]
        item = getattr(self.post, attrify(attr))
        if index.column() == 0:
            return attr
        else:
            return item

    def headerData(self, col, orientation, role=None):
        return QVariant('')


def attrify(attr):
    return attr.replace(' ', '_').lower()
