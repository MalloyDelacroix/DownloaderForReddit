# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UpdaterGUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_updater_gui(object):
    def setupUi(self, updater_gui):
        updater_gui.setObjectName("updater_gui")
        updater_gui.resize(527, 125)
        font = QtGui.QFont()
        font.setPointSize(10)
        updater_gui.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("update.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        updater_gui.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(updater_gui)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(updater_gui)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.progress_bar = QtWidgets.QProgressBar(updater_gui)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout.addWidget(self.progress_bar, 0, 0, 1, 1)
        self.button_box = QtWidgets.QDialogButtonBox(updater_gui)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.gridLayout.addWidget(self.button_box, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(updater_gui)
        QtCore.QMetaObject.connectSlotsByName(updater_gui)

    def retranslateUi(self, updater_gui):
        _translate = QtCore.QCoreApplication.translate
        updater_gui.setWindowTitle(_translate("updater_gui", "Downloader for Reddit Updater"))
        self.label.setText(_translate("updater_gui", "Please make sure The Downloader for Reddit is closed and press OK to begin the update"))

