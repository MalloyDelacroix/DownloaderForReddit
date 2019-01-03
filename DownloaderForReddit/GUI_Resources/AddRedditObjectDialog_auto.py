# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddRedditObjectDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_add_reddit_object_dialog(object):
    def setupUi(self, add_reddit_object_dialog):
        add_reddit_object_dialog.setObjectName("add_reddit_object_dialog")
        add_reddit_object_dialog.resize(389, 133)
        font = QtGui.QFont()
        font.setPointSize(10)
        add_reddit_object_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources/Images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        add_reddit_object_dialog.setWindowIcon(icon)
        self.vert_layout = QtWidgets.QVBoxLayout(add_reddit_object_dialog)
        self.vert_layout.setObjectName("vert_layout")
        self.label = QtWidgets.QLabel(add_reddit_object_dialog)
        self.label.setObjectName("label")
        self.vert_layout.addWidget(self.label)
        self.object_name_line_edit = QtWidgets.QLineEdit(add_reddit_object_dialog)
        self.object_name_line_edit.setObjectName("object_name_line_edit")
        self.vert_layout.addWidget(self.object_name_line_edit)
        self.ok_cancel_button_box = QtWidgets.QDialogButtonBox(add_reddit_object_dialog)
        self.ok_cancel_button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.ok_cancel_button_box.setObjectName("ok_cancel_button_box")
        self.vert_layout.addWidget(self.ok_cancel_button_box)

        self.retranslateUi(add_reddit_object_dialog)
        QtCore.QMetaObject.connectSlotsByName(add_reddit_object_dialog)

    def retranslateUi(self, add_reddit_object_dialog):
        _translate = QtCore.QCoreApplication.translate
        add_reddit_object_dialog.setWindowTitle(_translate("add_reddit_object_dialog", "Add User Dialog"))
        self.label.setText(_translate("add_reddit_object_dialog", "Enter a new user:"))

