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
import datetime

from Core import Injector
from Core.RedditObjects import RedditObject


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
        self.settings_manager = Injector.get_settings_manager()
        self.name = name
        self.list_type = list_type
        self.reddit_object_list = []

    def sort_lists(self, method):
        """
        Takes a tuple set by the view menu in the GUI, the first variable being the sort method and the second being
        the sort order (as an int which is interpreted as True or False), and sorts the display list accordingly
        Note: I know the lambda function below violates PEP8, but I don't care. That's how I'm doing it
        """
        if method[0] == 0:
            att_method = lambda x: getattr(x, 'name').lower()
        elif method[0] == 1:
            att_method = attrgetter('user_added')
        else:
            att_method = attrgetter('number_of_downloads')

        self.reddit_object_list = sorted(self.reddit_object_list, key=att_method,
                                         reverse=method[1])
        self.refresh()

    def insertRow(self, item, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.reddit_object_list.append(item)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for x in range(rows):
            self.reddit_object_list.remove(self.reddit_object_list[position])
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.reddit_object_list)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.reddit_object_list[index.row()].name
        elif role == Qt.DecorationRole:
            return None
        elif role == Qt.ToolTipRole:
            return self.set_tooltips(self.reddit_object_list[index.row()])
        elif role == Qt.EditRole:
            return self.reddit_object_list[index.row()].name

    def make_tool_tip(self, row):
        item = self.reddit_object_list[row]
        added_on = datetime.date.strftime(datetime.datetime.fromtimestamp(item.user_added),
                                          '%m-%d-%Y at %I:%M %p')
        if item.date_limit < 1136073600:
            last_download_date = 'No Date Available'
        else:
            last_download_date = datetime.date.strftime(datetime.datetime.fromtimestamp(item.date_limit),
                                                        '%m-%d-%Y at %I:%M %p')
        text = 'Total Downloads: %s\nLast Content Date: %s\nAdded On: %s' % (item.number_of_downloads,
                                                                             last_download_date, added_on)
        return text

    def set_tooltips(self, reddit_object):
        """
        Builds the tooltip text based on what options are selected in the settings manager and returns the text.
        :param reddit_object: The reddit object the tooltip text is based off of.
        :type reddit_object: RedditObject
        :return: Text formatted to be displayed as a tooltip.
        :rtype: str
        """
        tooltip_dict = {
            'name': 'Name: %s' % reddit_object.name,
            'do_not_edit': 'Do Not Edit: %s' % reddit_object.do_not_edit,
            'last_download_date': 'Last Download Date: %s' % (self.format_date(reddit_object.date_limit) if
                                                             reddit_object.date_limit > 1136073600 else
                                                             'No Last Download Date'),
            'custom_date_limit': 'Custom Date Limit: %s' % self.format_date(reddit_object.custom_date_limit),
            'post_limit': 'Post Limit: %s' % reddit_object.post_limit,
            'name_downloads_by': 'Name Downloads By: %s' % reddit_object.name_downloads_by,
            'subreddit_save_method': 'Subreddit Save Method: %s' % reddit_object.subreddit_save_method,
            'save_path': 'Save Path: %s' % reddit_object.save_directory,
            'download_videos': 'Download Videos: %s' % reddit_object.download_videos,
            'download_images': 'Download Images: %s' % reddit_object.download_images,
            'avoid_duplicates': 'Avoid Duplicates: %s' % reddit_object.avoid_duplicates,
            'nsfw_filter': 'NSFW Filter: %s' % reddit_object.name,  # TODO: revise this when attribute added
            'saved_content_count': 'Saved Content Count: %s' % len(reddit_object.saved_content),
            'saved_submission_count': 'Saved Submission Count: %s' % len(reddit_object.saved_submissions),
            'total_download_count': 'Total Downloads: %s' % reddit_object.number_of_downloads,
            'added_on_date': 'Date Added: %s' % self.format_date(reddit_object.user_added)
        }
        tooltip = ''
        for key, value in tooltip_dict.items():
            if self.settings_manager.tooltip_display_dict[key]:
                tooltip += '%s\n' % value
        return tooltip.strip()

    @staticmethod
    def format_date(epoch):
        if epoch is None:
            return 'None'
        if epoch < 86400:
            epoch = 86400
        return datetime.date.strftime(datetime.datetime.fromtimestamp(epoch), '%m-%d-%Y at %I:%M %p')

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
