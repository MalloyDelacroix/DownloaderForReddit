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


from operator import itemgetter
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt


class RedditObjectItemDisplayModel(QAbstractListModel):

    """
    A class that handles displaying data from a reddit objects previous downloads or saved content/submissions lists.
    """

    def __init__(self, selected_object, display_list):
        """
        Initializes the display model for displaying user content.
        :param selected_object: The currently selected reddit object who's lists are to be displayed.
        :param display_list: The current list that is to be displayed.
        """
        super().__init__()

        self.reddit_object = None
        self.content_display = None
        self.display_list = display_list

        self.set_reddit_object(selected_object)

    def set_reddit_object(self, reddit_object):
        self.reddit_object = reddit_object
        self.content_display = sorted([(value[1], key) for key, value in self.reddit_object.saved_content.items()],
                                      key=itemgetter(0))

    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the len of the content list which is used to determine the number of rows displayed in the list."""
        if self.display_list == 'previous_downloads':
            return len(self.reddit_object.previous_downloads)
        elif self.display_list == 'saved_submissions':
            return len(self.reddit_object.saved_submissions)
        else:
            return len(self.content_display)

    def removeRows(self, index_list, rows=None, parent=QModelIndex(), *args, **kwargs):
        """Removes the supplied indexes from the currently displayed list."""
        index_list.sort(reverse=True)
        if self.display_list == 'previous_downloads':
            self.remove_previous_downloaded(index_list, parent)
        elif self.display_list == 'saved_content':
            self.remove_saved_content(index_list, parent)
        else:
            self.remove_saved_submission(index_list, parent)
        return True

    def remove_previous_downloaded(self, index_list, parent):
        for x in index_list:
            self.beginRemoveRows(parent, x, x)
            del self.reddit_object.previous_downloads[x]
            self.endRemoveRows()

    def remove_saved_content(self, index_list, parent):
        for index in index_list:
            self.beginRemoveRows(parent, index, index)
            key = self.content_display[index][1]
            del self.content_display[index]
            del self.reddit_object.saved_content[key]
            self.endRemoveRows()

    def remove_saved_submission(self, index_list, parent):
        for x in index_list:
            self.beginRemoveRows(parent, x, x)
            del self.reddit_object.saved_submissions[x]
            self.endRemoveRows()

    def data(self, index, role=None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            index = index.row()
            if self.display_list == 'previous_downloads':
                return self.reddit_object.previous_downloads[index]
            elif self.display_list == 'saved_submissions':
                return self.reddit_object.saved_submissions[index].url  # TODO: show more info on click
            elif self.display_list == 'saved_content':
                item = self.content_display[index]
                return '%s:  %s' % (item[0], item[1])
            else:
                return None

    def flags(self, QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def refresh(self):
        first = self.createIndex(0, 0)
        second = self.createIndex(0, self.rowCount())
        self.dataChanged.emit(first, second)
