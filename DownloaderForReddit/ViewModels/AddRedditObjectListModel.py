from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
import logging


class AddRedditObjectListModel(QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.name_list = [None]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.name_list)

    def insertRow(self, name, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, self.rowCount() - 1, self.rowCount())
        self.name_list.append(name)
        self.endInsertRows()
        return True

    def removeRows(self, pos, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, pos, pos + rows - 1)
        for x in range(rows):
            self.name_list.remove(self.name_list[pos])
        self.endRemoveRows()
        return True

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.name_list[index.row()]
        elif role == Qt.DecorationRole:
            return None
