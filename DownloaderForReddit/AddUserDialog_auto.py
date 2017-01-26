# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddUserDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_add_user_dialog(object):
    def setupUi(self, add_user_dialog):
        add_user_dialog.setObjectName("add_user_dialog")
        add_user_dialog.resize(259, 98)
        font = QtGui.QFont()
        font.setPointSize(10)
        add_user_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        add_user_dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(add_user_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(add_user_dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.user_name_line_edit = QtWidgets.QLineEdit(add_user_dialog)
        self.user_name_line_edit.setObjectName("user_name_line_edit")
        self.gridLayout.addWidget(self.user_name_line_edit, 1, 0, 1, 2)
        self.add_another_button = QtWidgets.QPushButton(add_user_dialog)
        self.add_another_button.setObjectName("add_another_button")
        self.gridLayout.addWidget(self.add_another_button, 2, 0, 1, 1)
        self.ok_cancel_button_box = QtWidgets.QDialogButtonBox(add_user_dialog)
        self.ok_cancel_button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.ok_cancel_button_box.setObjectName("ok_cancel_button_box")
        self.gridLayout.addWidget(self.ok_cancel_button_box, 2, 1, 1, 1)

        self.retranslateUi(add_user_dialog)
        QtCore.QMetaObject.connectSlotsByName(add_user_dialog)

    def retranslateUi(self, add_user_dialog):
        _translate = QtCore.QCoreApplication.translate
        add_user_dialog.setWindowTitle(_translate("add_user_dialog", "Add User Dialog"))
        self.label.setText(_translate("add_user_dialog", "Enter a new user:"))
        self.add_another_button.setText(_translate("add_user_dialog", "Add Another"))

