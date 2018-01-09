# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FailedDownloadsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_failed_downloads_dialog(object):
    def setupUi(self, failed_downloads_dialog):
        failed_downloads_dialog.setObjectName("failed_downloads_dialog")
        failed_downloads_dialog.resize(659, 294)
        font = QtGui.QFont()
        font.setPointSize(10)
        failed_downloads_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".Images/failed_download.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        failed_downloads_dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(failed_downloads_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(failed_downloads_dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.auto_display_checkbox = QtWidgets.QCheckBox(failed_downloads_dialog)
        self.auto_display_checkbox.setObjectName("auto_display_checkbox")
        self.gridLayout.addWidget(self.auto_display_checkbox, 1, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(failed_downloads_dialog)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 2)

        self.retranslateUi(failed_downloads_dialog)
        QtCore.QMetaObject.connectSlotsByName(failed_downloads_dialog)

    def retranslateUi(self, failed_downloads_dialog):
        _translate = QtCore.QCoreApplication.translate
        failed_downloads_dialog.setWindowTitle(_translate("failed_downloads_dialog", "Failed Downloads"))
        self.auto_display_checkbox.setText(_translate("failed_downloads_dialog", "Do not automatically display this dialog"))

