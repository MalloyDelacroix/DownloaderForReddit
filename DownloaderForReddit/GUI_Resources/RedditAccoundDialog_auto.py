# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RedditAccountDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_reddit_account_dialog(object):
    def setupUi(self, reddit_account_dialog):
        reddit_account_dialog.setObjectName("reddit_account_dialog")
        reddit_account_dialog.resize(412, 108)
        font = QtGui.QFont()
        font.setPointSize(10)
        reddit_account_dialog.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(reddit_account_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.save_cancel_button_box = QtWidgets.QDialogButtonBox(reddit_account_dialog)
        self.save_cancel_button_box.setOrientation(QtCore.Qt.Horizontal)
        self.save_cancel_button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.save_cancel_button_box.setObjectName("save_cancel_button_box")
        self.gridLayout.addWidget(self.save_cancel_button_box, 1, 1, 1, 1)
        self.reddit_account_help_button = QtWidgets.QToolButton(reddit_account_dialog)
        self.reddit_account_help_button.setObjectName("reddit_account_help_button")
        self.gridLayout.addWidget(self.reddit_account_help_button, 1, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(reddit_account_dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.username_line_edit = QtWidgets.QLineEdit(reddit_account_dialog)
        self.username_line_edit.setObjectName("username_line_edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.username_line_edit)
        self.password_line_edit = QtWidgets.QLineEdit(reddit_account_dialog)
        self.password_line_edit.setObjectName("password_line_edit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.password_line_edit)
        self.label_2 = QtWidgets.QLabel(reddit_account_dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 2)

        self.retranslateUi(reddit_account_dialog)
        self.save_cancel_button_box.accepted.connect(reddit_account_dialog.accept)
        self.save_cancel_button_box.rejected.connect(reddit_account_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(reddit_account_dialog)

    def retranslateUi(self, reddit_account_dialog):
        _translate = QtCore.QCoreApplication.translate
        reddit_account_dialog.setWindowTitle(_translate("reddit_account_dialog", "Reddit Account Dialog"))
        self.reddit_account_help_button.setText(_translate("reddit_account_dialog", "?"))
        self.label.setText(_translate("reddit_account_dialog", "Reddit Username:"))
        self.label_2.setText(_translate("reddit_account_dialog", "Reddit Password:"))

