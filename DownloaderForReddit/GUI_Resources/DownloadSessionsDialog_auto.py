# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DownloadSessionsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DownloadSessionDialog(object):
    def setupUi(self, DownloadSessionDialog):
        DownloadSessionDialog.setObjectName("DownloadSessionDialog")
        DownloadSessionDialog.resize(1689, 919)
        self.verticalLayout = QtWidgets.QVBoxLayout(DownloadSessionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.show_reddit_objects_checkbox = QtWidgets.QCheckBox(DownloadSessionDialog)
        self.show_reddit_objects_checkbox.setObjectName("show_reddit_objects_checkbox")
        self.horizontalLayout.addWidget(self.show_reddit_objects_checkbox)
        self.show_posts_checkbox = QtWidgets.QCheckBox(DownloadSessionDialog)
        self.show_posts_checkbox.setObjectName("show_posts_checkbox")
        self.horizontalLayout.addWidget(self.show_posts_checkbox)
        self.show_content_checkbox = QtWidgets.QCheckBox(DownloadSessionDialog)
        self.show_content_checkbox.setObjectName("show_content_checkbox")
        self.horizontalLayout.addWidget(self.show_content_checkbox)
        self.show_comments_checkbox = QtWidgets.QCheckBox(DownloadSessionDialog)
        self.show_comments_checkbox.setObjectName("show_comments_checkbox")
        self.horizontalLayout.addWidget(self.show_comments_checkbox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtWidgets.QSplitter(DownloadSessionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.download_session_list_view = QtWidgets.QListView(self.splitter)
        self.download_session_list_view.setObjectName("download_session_list_view")
        self.reddit_object_list_view = QtWidgets.QListView(self.splitter)
        self.reddit_object_list_view.setObjectName("reddit_object_list_view")
        self.post_table_view = QtWidgets.QTableView(self.splitter)
        self.post_table_view.setObjectName("post_table_view")
        self.content_list_view = QtWidgets.QListView(self.splitter)
        self.content_list_view.setObjectName("content_list_view")
        self.comment_tree_view = QtWidgets.QTreeView(self.splitter)
        self.comment_tree_view.setObjectName("comment_tree_view")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(DownloadSessionDialog)
        QtCore.QMetaObject.connectSlotsByName(DownloadSessionDialog)

    def retranslateUi(self, DownloadSessionDialog):
        _translate = QtCore.QCoreApplication.translate
        DownloadSessionDialog.setWindowTitle(_translate("DownloadSessionDialog", "Download Sessions"))
        self.show_reddit_objects_checkbox.setText(_translate("DownloadSessionDialog", "Show reddit objects"))
        self.show_posts_checkbox.setText(_translate("DownloadSessionDialog", "Show posts"))
        self.show_content_checkbox.setText(_translate("DownloadSessionDialog", "Show content"))
        self.show_comments_checkbox.setText(_translate("DownloadSessionDialog", "Show comments"))

