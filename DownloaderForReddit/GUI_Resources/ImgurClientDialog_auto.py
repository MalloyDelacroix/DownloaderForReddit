# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImgurClientDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_imgur_client_dialog(object):
    def setupUi(self, imgur_client_dialog):
        imgur_client_dialog.setObjectName("imgur_client_dialog")
        imgur_client_dialog.resize(412, 108)
        font = QtGui.QFont()
        font.setPointSize(10)
        imgur_client_dialog.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(imgur_client_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(imgur_client_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.imgur_client_help_button = QtWidgets.QToolButton(imgur_client_dialog)
        self.imgur_client_help_button.setObjectName("imgur_client_help_button")
        self.gridLayout.addWidget(self.imgur_client_help_button, 1, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(imgur_client_dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEdit = QtWidgets.QLineEdit(imgur_client_dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(imgur_client_dialog)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.label_2 = QtWidgets.QLabel(imgur_client_dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 2)

        self.retranslateUi(imgur_client_dialog)
        self.buttonBox.accepted.connect(imgur_client_dialog.accept)
        self.buttonBox.rejected.connect(imgur_client_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(imgur_client_dialog)

    def retranslateUi(self, imgur_client_dialog):
        _translate = QtCore.QCoreApplication.translate
        imgur_client_dialog.setWindowTitle(_translate("imgur_client_dialog", "Imgur Client Dialog"))
        self.imgur_client_help_button.setText(_translate("imgur_client_dialog", "?"))
        self.label.setText(_translate("imgur_client_dialog", "Imgur Client_Id:"))
        self.label_2.setText(_translate("imgur_client_dialog", "Imgur Client_Secret:"))

