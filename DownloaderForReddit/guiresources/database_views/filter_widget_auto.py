# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Kyle/PycharmProjects/DownloaderForReddit/Resources/ui_files//database_views/filter_widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FilterWidget(object):
    def setupUi(self, FilterWidget):
        FilterWidget.setObjectName("FilterWidget")
        FilterWidget.resize(350, 850)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FilterWidget.sizePolicy().hasHeightForWidth())
        FilterWidget.setSizePolicy(sizePolicy)
        FilterWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        FilterWidget.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.filter_input_widget = FilterInputWidget(FilterWidget)
        self.filter_input_widget.setObjectName("filter_input_widget")
        self.verticalLayout.addWidget(self.filter_input_widget)
        self.filter_box_list_widget = QtWidgets.QListWidget(FilterWidget)
        self.filter_box_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.filter_box_list_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.filter_box_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.filter_box_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.filter_box_list_widget.setMovement(QtWidgets.QListView.Static)
        self.filter_box_list_widget.setFlow(QtWidgets.QListView.TopToBottom)
        self.filter_box_list_widget.setProperty("isWrapping", True)
        self.filter_box_list_widget.setResizeMode(QtWidgets.QListView.Fixed)
        self.filter_box_list_widget.setLayoutMode(QtWidgets.QListView.Batched)
        self.filter_box_list_widget.setViewMode(QtWidgets.QListView.ListMode)
        self.filter_box_list_widget.setUniformItemSizes(False)
        self.filter_box_list_widget.setBatchSize(1)
        self.filter_box_list_widget.setWordWrap(False)
        self.filter_box_list_widget.setSelectionRectVisible(False)
        self.filter_box_list_widget.setObjectName("filter_box_list_widget")
        self.verticalLayout.addWidget(self.filter_box_list_widget)

        self.retranslateUi(FilterWidget)
        QtCore.QMetaObject.connectSlotsByName(FilterWidget)

    def retranslateUi(self, FilterWidget):
        _translate = QtCore.QCoreApplication.translate
        FilterWidget.setWindowTitle(_translate("FilterWidget", "Filter"))
from DownloaderForReddit.gui.database_views.filter_input_widget import FilterInputWidget
