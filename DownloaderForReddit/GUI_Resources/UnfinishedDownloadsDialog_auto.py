# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UnfinishedDownloadsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_unfinished_downloads_dialog(object):
    def setupUi(self, unfinished_downloads_dialog):
        unfinished_downloads_dialog.setObjectName("unfinished_downloads_dialog")
        unfinished_downloads_dialog.resize(414, 96)
        font = QtGui.QFont()
        font.setPointSize(10)
        unfinished_downloads_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources/Images/RedditDownloaderIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        unfinished_downloads_dialog.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(unfinished_downloads_dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(unfinished_downloads_dialog)
        self.label.setText("")
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 4)
        self.close_and_keep_button = QtWidgets.QPushButton(unfinished_downloads_dialog)
        self.close_and_keep_button.setObjectName("close_and_keep_button")
        self.gridLayout_2.addWidget(self.close_and_keep_button, 1, 3, 1, 1)
        self.close_and_delete_button = QtWidgets.QPushButton(unfinished_downloads_dialog)
        self.close_and_delete_button.setObjectName("close_and_delete_button")
        self.gridLayout_2.addWidget(self.close_and_delete_button, 1, 2, 1, 1)
        self.download_button = QtWidgets.QPushButton(unfinished_downloads_dialog)
        self.download_button.setObjectName("download_button")
        self.gridLayout_2.addWidget(self.download_button, 1, 0, 1, 1)

        self.retranslateUi(unfinished_downloads_dialog)
        QtCore.QMetaObject.connectSlotsByName(unfinished_downloads_dialog)

    def retranslateUi(self, unfinished_downloads_dialog):
        _translate = QtCore.QCoreApplication.translate
        unfinished_downloads_dialog.setWindowTitle(_translate("unfinished_downloads_dialog", "Unfinished Downloads"))
        self.close_and_keep_button.setToolTip(_translate("unfinished_downloads_dialog", "Closes this dialog but does not erase the list of unfinished downloads.  More unfinished downloads will be added to the list if another download is canceled"))
        self.close_and_keep_button.setText(_translate("unfinished_downloads_dialog", "Close"))
        self.close_and_delete_button.setToolTip(_translate("unfinished_downloads_dialog", "Closes this dialog and deletes the unfinished downloads list"))
        self.close_and_delete_button.setText(_translate("unfinished_downloads_dialog", "Delete List"))
        self.download_button.setToolTip(_translate("unfinished_downloads_dialog", "Closes this dialog and downloads the unfinished downloads list"))
        self.download_button.setText(_translate("unfinished_downloads_dialog", "Download List"))

