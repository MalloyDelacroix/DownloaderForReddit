# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\update_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_update_dialog_box(object):
    def setupUi(self, update_dialog_box):
        update_dialog_box.setObjectName("update_dialog_box")
        update_dialog_box.resize(794, 207)
        font = QtGui.QFont()
        font.setPointSize(10)
        update_dialog_box.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources\\ui_files\\../Resources/Images/update.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        update_dialog_box.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(update_dialog_box)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(update_dialog_box)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.do_not_notify_checkbox = QtWidgets.QCheckBox(update_dialog_box)
        self.do_not_notify_checkbox.setObjectName("do_not_notify_checkbox")
        self.gridLayout.addWidget(self.do_not_notify_checkbox, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(update_dialog_box)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.link_label = QtWidgets.QLabel(update_dialog_box)
        self.link_label.setObjectName("link_label")
        self.gridLayout.addWidget(self.link_label, 1, 0, 1, 1)
        self.direct_link_label = QtWidgets.QLabel(update_dialog_box)
        self.direct_link_label.setObjectName("direct_link_label")
        self.gridLayout.addWidget(self.direct_link_label, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(update_dialog_box)
        self.buttonBox.accepted.connect(update_dialog_box.accept)
        self.buttonBox.rejected.connect(update_dialog_box.reject)
        QtCore.QMetaObject.connectSlotsByName(update_dialog_box)

    def retranslateUi(self, update_dialog_box):
        _translate = QtCore.QCoreApplication.translate
        update_dialog_box.setWindowTitle(_translate("update_dialog_box", "Update"))
        self.label.setText(_translate("update_dialog_box", "TextLabel"))
        self.do_not_notify_checkbox.setText(_translate("update_dialog_box", "Do not notify me about this update again"))
        self.link_label.setText(_translate("update_dialog_box", "TextLabel"))
        self.direct_link_label.setText(_translate("update_dialog_box", "TextLabel"))
