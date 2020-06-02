# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DownloadSettingsWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DownloadSettingsWidget(object):
    def setupUi(self, DownloadSettingsWidget):
        DownloadSettingsWidget.setObjectName("DownloadSettingsWidget")
        DownloadSettingsWidget.resize(906, 709)
        self.verticalLayout = QtWidgets.QVBoxLayout(DownloadSettingsWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_widget = QtWidgets.QListWidget(DownloadSettingsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_widget.sizePolicy().hasHeightForWidth())
        self.list_widget.setSizePolicy(sizePolicy)
        self.list_widget.setObjectName("list_widget")
        self.horizontalLayout.addWidget(self.list_widget)
        self.scrollArea = QtWidgets.QScrollArea(DownloadSettingsWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 611, 679))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.list_settings_widget = ObjectSettingsWidget(self.scrollAreaWidgetContents)
        self.list_settings_widget.setObjectName("list_settings_widget")
        self.verticalLayout_2.addWidget(self.list_settings_widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DownloadSettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(DownloadSettingsWidget)

    def retranslateUi(self, DownloadSettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        DownloadSettingsWidget.setWindowTitle(_translate("DownloadSettingsWidget", "Download Settings"))
from DownloaderForReddit.GUI.widgets.ObjectSettingsWidget import ObjectSettingsWidget
