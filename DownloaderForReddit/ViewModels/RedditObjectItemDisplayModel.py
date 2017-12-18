from operator import itemgetter
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt


class RedditObjectItemDisplayModel(QAbstractListModel):

    def __init__(self, selected_object, display_list):
        super().__init__()

        self.reddit_object = selected_object
        self.content_display = sorted([(value[1], key) for key, value in self.reddit_object.saved_content.items()],
                                      key=itemgetter(0))
        self.display_list = display_list

    def rowCount(self, parent=None, *args, **kwargs):
        if self.display_list == 'previous_downloads':
            return len(self.reddit_object.previous_downloads)
        elif self.display_list == 'saved_submissions':
            return len(self.reddit_object.saved_submissions)
        else:
            return len(self.content_display)

    def removeRows(self, index_list, rows=None, parent=QModelIndex(), *args, **kwargs):
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
        if role == Qt.DisplayRole:
            index = index.row()
            if self.display_list == 'previous_downloads':
                return self.reddit_object.previous_downloads[index]
            elif self.display_list == 'saved_submissions':
                return self.reddit_object.saved_submissions[index]
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





















