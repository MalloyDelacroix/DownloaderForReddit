# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\settings\notification_settings_widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NotificationSettingsWidget(object):
    def setupUi(self, NotificationSettingsWidget):
        NotificationSettingsWidget.setObjectName("NotificationSettingsWidget")
        NotificationSettingsWidget.resize(907, 709)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NotificationSettingsWidget)
        self.verticalLayout_2.setSpacing(30)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(NotificationSettingsWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.update_level_combo = QtWidgets.QComboBox(NotificationSettingsWidget)
        self.update_level_combo.setMinimumSize(QtCore.QSize(200, 0))
        self.update_level_combo.setObjectName("update_level_combo")
        self.horizontalLayout.addWidget(self.update_level_combo)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.auto_display_failed_downloads_checkbox = QtWidgets.QCheckBox(NotificationSettingsWidget)
        self.auto_display_failed_downloads_checkbox.setObjectName("auto_display_failed_downloads_checkbox")
        self.verticalLayout_2.addWidget(self.auto_display_failed_downloads_checkbox)
        self.groupBox = QtWidgets.QGroupBox(NotificationSettingsWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.remove_reddit_object_warning_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.remove_reddit_object_warning_checkbox.setObjectName("remove_reddit_object_warning_checkbox")
        self.verticalLayout.addWidget(self.remove_reddit_object_warning_checkbox)
        self.remove_reddit_object_list_warning_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.remove_reddit_object_list_warning_checkbox.setObjectName("remove_reddit_object_list_warning_checkbox")
        self.verticalLayout.addWidget(self.remove_reddit_object_list_warning_checkbox)
        self.large_post_update_warning_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.large_post_update_warning_checkbox.setObjectName("large_post_update_warning_checkbox")
        self.verticalLayout.addWidget(self.large_post_update_warning_checkbox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(NotificationSettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(NotificationSettingsWidget)

    def retranslateUi(self, NotificationSettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        NotificationSettingsWidget.setWindowTitle(_translate("NotificationSettingsWidget", "Notification Settings"))
        self.label.setToolTip(_translate("NotificationSettingsWidget", "<html><head/><body><p>This is the update level at which an update must be before you will be notified of its release</p></body></html>"))
        self.label.setText(_translate("NotificationSettingsWidget", "Update notification level:"))
        self.auto_display_failed_downloads_checkbox.setText(_translate("NotificationSettingsWidget", "Show failed downloads dialog after download"))
        self.groupBox.setTitle(_translate("NotificationSettingsWidget", "Notification Dialogs"))
        self.remove_reddit_object_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before removing user/subreddit"))
        self.remove_reddit_object_list_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before removing list"))
        self.large_post_update_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before updating large number of posts"))
