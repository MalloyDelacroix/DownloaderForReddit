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
        self.notify_available_updates_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.notify_available_updates_checkbox.setObjectName("notify_available_updates_checkbox")
        self.verticalLayout.addWidget(self.notify_available_updates_checkbox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(NotificationSettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(NotificationSettingsWidget)

    def retranslateUi(self, NotificationSettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        NotificationSettingsWidget.setWindowTitle(_translate("NotificationSettingsWidget", "Notification Settings"))
        self.auto_display_failed_downloads_checkbox.setText(_translate("NotificationSettingsWidget", "Show failed downloads dialog after download"))
        self.groupBox.setTitle(_translate("NotificationSettingsWidget", "Notification Dialogs"))
        self.remove_reddit_object_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before removing user/subreddit"))
        self.remove_reddit_object_list_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before removing list"))
        self.large_post_update_warning_checkbox.setText(_translate("NotificationSettingsWidget", "Ask before updating large number of posts"))
        self.notify_available_updates_checkbox.setText(_translate("NotificationSettingsWidget", "Notify of available updates"))
