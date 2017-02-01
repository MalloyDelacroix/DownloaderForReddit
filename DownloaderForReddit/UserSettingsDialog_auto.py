# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UserSettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_user_settings_dialog(object):
    def setupUi(self, user_settings_dialog):
        user_settings_dialog.setObjectName("user_settings_dialog")
        user_settings_dialog.resize(505, 511)
        font = QtGui.QFont()
        font.setPointSize(10)
        user_settings_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("pictures/settings_three_gears.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        user_settings_dialog.setWindowIcon(icon)
        user_settings_dialog.setModal(False)
        self.gridLayout_5 = QtWidgets.QGridLayout(user_settings_dialog)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setContentsMargins(0, -1, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.user_list_widget = QtWidgets.QListWidget(user_settings_dialog)
        self.user_list_widget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.user_list_widget.setFont(font)
        self.user_list_widget.setObjectName("user_list_widget")
        self.gridLayout.addWidget(self.user_list_widget, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.save_cancel_buton_box = QtWidgets.QDialogButtonBox(user_settings_dialog)
        self.save_cancel_buton_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.save_cancel_buton_box.setObjectName("save_cancel_buton_box")
        self.gridLayout_5.addWidget(self.save_cancel_buton_box, 1, 2, 1, 1)
        self.restore_defaults_button = QtWidgets.QPushButton(user_settings_dialog)
        self.restore_defaults_button.setObjectName("restore_defaults_button")
        self.gridLayout_5.addWidget(self.restore_defaults_button, 1, 0, 1, 1)
        self.view_downloads_button = QtWidgets.QPushButton(user_settings_dialog)
        self.view_downloads_button.setObjectName("view_downloads_button")
        self.gridLayout_5.addWidget(self.view_downloads_button, 1, 1, 1, 1)
        self.stacked_widget = QtWidgets.QStackedWidget(user_settings_dialog)
        self.stacked_widget.setObjectName("stacked_widget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.page)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.date_limit_edit = QtWidgets.QDateTimeEdit(self.page)
        self.date_limit_edit.setCalendarPopup(True)
        self.date_limit_edit.setTimeSpec(QtCore.Qt.LocalTime)
        self.date_limit_edit.setObjectName("date_limit_edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.date_limit_edit)
        self.label_2 = QtWidgets.QLabel(self.page)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.name_downloads_combo = QtWidgets.QComboBox(self.page)
        self.name_downloads_combo.setObjectName("name_downloads_combo")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.name_downloads_combo)
        self.label_4 = QtWidgets.QLabel(self.page)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.avoid_duplicates_checkbox = QtWidgets.QCheckBox(self.page)
        self.avoid_duplicates_checkbox.setObjectName("avoid_duplicates_checkbox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.avoid_duplicates_checkbox)
        self.cust_save_path_dialog = QtWidgets.QPushButton(self.page)
        self.cust_save_path_dialog.setObjectName("cust_save_path_dialog")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.cust_save_path_dialog)
        self.custom_save_path_line_edit = QtWidgets.QLineEdit(self.page)
        self.custom_save_path_line_edit.setObjectName("custom_save_path_line_edit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.custom_save_path_line_edit)
        self.download_videos_checkbox = QtWidgets.QCheckBox(self.page)
        self.download_videos_checkbox.setObjectName("download_videos_checkbox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.download_videos_checkbox)
        self.download_images_checkbox = QtWidgets.QCheckBox(self.page)
        self.download_images_checkbox.setObjectName("download_images_checkbox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.download_images_checkbox)
        self.restrict_date_checkbox = QtWidgets.QCheckBox(self.page)
        self.restrict_date_checkbox.setObjectName("restrict_date_checkbox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.restrict_date_checkbox)
        self.label = QtWidgets.QLabel(self.page)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.post_limit_spinbox = QtWidgets.QSpinBox(self.page)
        self.post_limit_spinbox.setAccelerated(True)
        self.post_limit_spinbox.setMaximum(1000)
        self.post_limit_spinbox.setObjectName("post_limit_spinbox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.post_limit_spinbox)
        self.gridLayout_4.addLayout(self.formLayout, 1, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.previous_downloads_list = QtWidgets.QTextBrowser(self.page)
        self.previous_downloads_list.setObjectName("previous_downloads_list")
        self.gridLayout_2.addWidget(self.previous_downloads_list, 0, 0, 1, 3)
        self.label_3 = QtWidgets.QLabel(self.page)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.user_downloads_label = QtWidgets.QLabel(self.page)
        self.user_downloads_label.setObjectName("user_downloads_label")
        self.gridLayout_2.addWidget(self.user_downloads_label, 1, 1, 1, 1)
        self.user_added_label = QtWidgets.QLabel(self.page)
        self.user_added_label.setObjectName("user_added_label")
        self.gridLayout_2.addWidget(self.user_added_label, 2, 0, 1, 3)
        self.gridLayout_4.addLayout(self.gridLayout_2, 2, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.download_user_button = QtWidgets.QPushButton(self.page)
        self.download_user_button.setObjectName("download_user_button")
        self.gridLayout_3.addWidget(self.download_user_button, 0, 0, 1, 1)
        self.do_not_edit_checkbox = QtWidgets.QCheckBox(self.page)
        self.do_not_edit_checkbox.setObjectName("do_not_edit_checkbox")
        self.gridLayout_3.addWidget(self.do_not_edit_checkbox, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.stacked_widget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.user_content_list = QtWidgets.QListWidget(self.page_2)
        self.user_content_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.user_content_list.setResizeMode(QtWidgets.QListView.Adjust)
        self.user_content_list.setViewMode(QtWidgets.QListView.IconMode)
        self.user_content_list.setWordWrap(True)
        self.user_content_list.setObjectName("user_content_list")
        self.gridLayout_6.addWidget(self.user_content_list, 0, 0, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.stacked_widget.addWidget(self.page_2)
        self.gridLayout_5.addWidget(self.stacked_widget, 0, 1, 1, 2)

        self.retranslateUi(user_settings_dialog)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(user_settings_dialog)

    def retranslateUi(self, user_settings_dialog):
        _translate = QtCore.QCoreApplication.translate
        user_settings_dialog.setWindowTitle(_translate("user_settings_dialog", "User Settings"))
        self.restore_defaults_button.setToolTip(_translate("user_settings_dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Restore settings to the options in the master settings dialog</span></p></body></html>"))
        self.restore_defaults_button.setText(_translate("user_settings_dialog", "Restore Defaults"))
        self.view_downloads_button.setToolTip(_translate("user_settings_dialog", "View this users downloads (will only display downloads that are in the save path above)"))
        self.view_downloads_button.setText(_translate("user_settings_dialog", "View Downloads"))
        self.date_limit_edit.setToolTip(_translate("user_settings_dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">The date and time (time is in 24 hour format) to restrict downloads to</span></p></body></html>"))
        self.date_limit_edit.setDisplayFormat(_translate("user_settings_dialog", "M/d/yyyy hh:mm ap"))
        self.label_2.setText(_translate("user_settings_dialog", "Name Downloads By: "))
        self.label_4.setText(_translate("user_settings_dialog", "Previous Downloads:"))
        self.avoid_duplicates_checkbox.setText(_translate("user_settings_dialog", "Avoid Duplicates"))
        self.cust_save_path_dialog.setText(_translate("user_settings_dialog", "Custom Save Path"))
        self.download_videos_checkbox.setText(_translate("user_settings_dialog", "Download Videos"))
        self.download_images_checkbox.setText(_translate("user_settings_dialog", "Download Images"))
        self.restrict_date_checkbox.setText(_translate("user_settings_dialog", "Restrict by Date:"))
        self.label.setText(_translate("user_settings_dialog", "Post Limit:"))
        self.label_3.setText(_translate("user_settings_dialog", "Total User Downloads: "))
        self.user_downloads_label.setText(_translate("user_settings_dialog", "0"))
        self.user_added_label.setText(_translate("user_settings_dialog", "User Added On:"))
        self.download_user_button.setToolTip(_translate("user_settings_dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Download this user only with the settings as they are in this dialog</span></p></body></html>"))
        self.download_user_button.setText(_translate("user_settings_dialog", "Download This User"))
        self.do_not_edit_checkbox.setToolTip(_translate("user_settings_dialog", "<html><head/><body><p><span style=\" font-size:10pt;\">If checked the changes made in this dialog will not be overwritten by the program when it is run.  The user date limit, avoid duplicates , and download naming method will all remain as they are when this dialog is saved.  The previous downloads will continue to be added to.</span></p></body></html>"))
        self.do_not_edit_checkbox.setText(_translate("user_settings_dialog", "Do not overwrite these settings"))

