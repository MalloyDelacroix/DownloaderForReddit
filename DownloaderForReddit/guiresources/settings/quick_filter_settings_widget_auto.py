# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\settings\quick_filter_settings_widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QuickFilterSettingsWidget(object):
    def setupUi(self, QuickFilterSettingsWidget):
        QuickFilterSettingsWidget.setObjectName("QuickFilterSettingsWidget")
        QuickFilterSettingsWidget.resize(906, 709)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(QuickFilterSettingsWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(QuickFilterSettingsWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.add_new_quick_filter_button = QtWidgets.QPushButton(self.widget)
        self.add_new_quick_filter_button.setObjectName("add_new_quick_filter_button")
        self.verticalLayout_2.addWidget(self.add_new_quick_filter_button)
        self.name_list_widget = QtWidgets.QListWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_list_widget.sizePolicy().hasHeightForWidth())
        self.name_list_widget.setSizePolicy(sizePolicy)
        self.name_list_widget.setObjectName("name_list_widget")
        self.verticalLayout_2.addWidget(self.name_list_widget)
        self.widget1 = QtWidgets.QWidget(self.splitter)
        self.widget1.setObjectName("widget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.filter_input_widget = FilterInputWidget(self.widget1)
        self.filter_input_widget.setObjectName("filter_input_widget")
        self.verticalLayout.addWidget(self.filter_input_widget)
        self.filter_list_widget = QtWidgets.QListWidget(self.widget1)
        self.filter_list_widget.setMovement(QtWidgets.QListView.Static)
        self.filter_list_widget.setLayoutMode(QtWidgets.QListView.Batched)
        self.filter_list_widget.setViewMode(QtWidgets.QListView.ListMode)
        self.filter_list_widget.setBatchSize(5)
        self.filter_list_widget.setObjectName("filter_list_widget")
        self.verticalLayout.addWidget(self.filter_list_widget)
        self.verticalLayout_3.addWidget(self.splitter)

        self.retranslateUi(QuickFilterSettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(QuickFilterSettingsWidget)

    def retranslateUi(self, QuickFilterSettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        QuickFilterSettingsWidget.setWindowTitle(_translate("QuickFilterSettingsWidget", "Quick Filter Settings"))
        self.add_new_quick_filter_button.setText(_translate("QuickFilterSettingsWidget", "Add Quick Filter"))
from DownloaderForReddit.gui.database_views.filter_input_widget import FilterInputWidget
