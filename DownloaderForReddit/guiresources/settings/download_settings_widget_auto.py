# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\settings\download_settings_widget.ui'
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
        self.cascade_changes_checkbox = QtWidgets.QCheckBox(DownloadSettingsWidget)
        self.cascade_changes_checkbox.setObjectName("cascade_changes_checkbox")
        self.verticalLayout.addWidget(self.cascade_changes_checkbox)
        self.splitter = QtWidgets.QSplitter(DownloadSettingsWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.list_widget = QtWidgets.QListWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_widget.sizePolicy().hasHeightForWidth())
        self.list_widget.setSizePolicy(sizePolicy)
        self.list_widget.setBaseSize(QtCore.QSize(200, 0))
        self.list_widget.setObjectName("list_widget")
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 105, 649))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.list_settings_widget = ObjectSettingsWidget(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_settings_widget.sizePolicy().hasHeightForWidth())
        self.list_settings_widget.setSizePolicy(sizePolicy)
        self.list_settings_widget.setObjectName("list_settings_widget")
        self.verticalLayout_2.addWidget(self.list_settings_widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(DownloadSettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(DownloadSettingsWidget)

    def retranslateUi(self, DownloadSettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        DownloadSettingsWidget.setWindowTitle(_translate("DownloadSettingsWidget", "Download Default Settings"))
        self.cascade_changes_checkbox.setToolTip(_translate("DownloadSettingsWidget", "<html><head/><body><p>When selected, changes that are made to the selected list will cascade down to each user/subreddit in the list unless that user/subreddit has its settings locked</p></body></html>"))
        self.cascade_changes_checkbox.setText(_translate("DownloadSettingsWidget", "Cascade changes"))
from DownloaderForReddit.gui.widgets.object_settings_widget import ObjectSettingsWidget
