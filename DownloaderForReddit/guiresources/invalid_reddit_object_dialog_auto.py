# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\invalid_reddit_object_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InvalidRedditObjectDialog(object):
    def setupUi(self, InvalidRedditObjectDialog):
        InvalidRedditObjectDialog.setObjectName("InvalidRedditObjectDialog")
        InvalidRedditObjectDialog.resize(596, 651)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(InvalidRedditObjectDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(InvalidRedditObjectDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.decision_box = QtWidgets.QVBoxLayout()
        self.decision_box.setObjectName("decision_box")
        self.select_all_checkbox = QtWidgets.QCheckBox(InvalidRedditObjectDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.select_all_checkbox.setFont(font)
        self.select_all_checkbox.setObjectName("select_all_checkbox")
        self.decision_box.addWidget(self.select_all_checkbox)
        self.decision_list = QtWidgets.QListWidget(InvalidRedditObjectDialog)
        self.decision_list.setObjectName("decision_list")
        self.decision_box.addWidget(self.decision_list)
        self.line = QtWidgets.QFrame(InvalidRedditObjectDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.decision_box.addWidget(self.line)
        self.verticalLayout.addLayout(self.decision_box)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.button_box = QtWidgets.QDialogButtonBox(InvalidRedditObjectDialog)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.verticalLayout_2.addWidget(self.button_box)

        self.retranslateUi(InvalidRedditObjectDialog)
        QtCore.QMetaObject.connectSlotsByName(InvalidRedditObjectDialog)

    def retranslateUi(self, InvalidRedditObjectDialog):
        _translate = QtCore.QCoreApplication.translate
        InvalidRedditObjectDialog.setWindowTitle(_translate("InvalidRedditObjectDialog", "Invalid Reddit Objects"))
        self.label.setText(_translate("InvalidRedditObjectDialog", "<html><head/><body><p>The following users/subreddits are not valid. They have either been deleted, or banned/suspended by reddit. </p><p>How would you like to handle these users/subreddits?</p></body></html>"))
        self.select_all_checkbox.setText(_translate("InvalidRedditObjectDialog", "Select All"))
