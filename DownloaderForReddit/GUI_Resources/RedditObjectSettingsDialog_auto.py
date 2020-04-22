# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RedditObjectSettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RedditObjectSettingsDialog(object):
    def setupUi(self, RedditObjectSettingsDialog):
        RedditObjectSettingsDialog.setObjectName("RedditObjectSettingsDialog")
        RedditObjectSettingsDialog.resize(773, 940)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(RedditObjectSettingsDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(RedditObjectSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.reddit_objects_list_view = QtWidgets.QListView(self.splitter)
        self.reddit_objects_list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.reddit_objects_list_view.setObjectName("reddit_objects_list_view")
        self.scroll_area = QtWidgets.QScrollArea(self.splitter)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area_contents = QtWidgets.QWidget()
        self.scroll_area_contents.setGeometry(QtCore.QRect(0, 0, 262, 867))
        self.scroll_area_contents.setObjectName("scroll_area_contents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scroll_area_contents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.download_button = QtWidgets.QPushButton(self.scroll_area_contents)
        self.download_button.setObjectName("download_button")
        self.verticalLayout.addWidget(self.download_button)
        self.line_2 = QtWidgets.QFrame(self.scroll_area_contents)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.info_widget = ObjectInfoWidget(self.scroll_area_contents)
        self.info_widget.setObjectName("info_widget")
        self.verticalLayout.addWidget(self.info_widget)
        self.line = QtWidgets.QFrame(self.scroll_area_contents)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.settings_widget = ObjectSettingsWidget(self.scroll_area_contents)
        self.settings_widget.setObjectName("settings_widget")
        self.verticalLayout.addWidget(self.settings_widget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.verticalLayout_3.addWidget(self.splitter)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.reset_button = QtWidgets.QPushButton(RedditObjectSettingsDialog)
        self.reset_button.setObjectName("reset_button")
        self.horizontalLayout.addWidget(self.reset_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.dialog_button_box = QtWidgets.QDialogButtonBox(RedditObjectSettingsDialog)
        self.dialog_button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.dialog_button_box.setCenterButtons(False)
        self.dialog_button_box.setObjectName("dialog_button_box")
        self.horizontalLayout.addWidget(self.dialog_button_box)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(RedditObjectSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(RedditObjectSettingsDialog)

    def retranslateUi(self, RedditObjectSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        RedditObjectSettingsDialog.setWindowTitle(_translate("RedditObjectSettingsDialog", "Settings"))
        self.download_button.setText(_translate("RedditObjectSettingsDialog", "Download "))
        self.reset_button.setText(_translate("RedditObjectSettingsDialog", "Reset"))

from DownloaderForReddit.GUI.widgets.ObjectInfoWidget import ObjectInfoWidget
from DownloaderForReddit.GUI.widgets.ObjectSettingsWidget import ObjectSettingsWidget
