# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI_Resources/AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(413, 491)
        About.setMinimumSize(QtCore.QSize(365, 230))
        About.setMaximumSize(QtCore.QSize(1000, 1000))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources/Images/RedditDownloaderIcon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        About.setWindowIcon(icon)
        self.gridLayout_3 = QtWidgets.QGridLayout(About)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.info_label = QtWidgets.QLabel(About)
        self.info_label.setObjectName("info_label")
        self.gridLayout.addWidget(self.info_label, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(About)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.link_label = QtWidgets.QLabel(About)
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setObjectName("link_label")
        self.gridLayout.addWidget(self.link_label, 2, 1, 1, 1)
        self.logo_label = QtWidgets.QLabel(About)
        self.logo_label.setObjectName("logo_label")
        self.gridLayout.addWidget(self.logo_label, 0, 0, 3, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.license_box = QtWidgets.QTextBrowser(About)
        self.license_box.setObjectName("license_box")
        self.gridLayout_2.addWidget(self.license_box, 0, 0, 1, 2)
        self.total_downloads_label = QtWidgets.QLabel(About)
        self.total_downloads_label.setObjectName("total_downloads_label")
        self.gridLayout_2.addWidget(self.total_downloads_label, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(About)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 1, 0, 1, 1)

        self.retranslateUi(About)
        self.buttonBox.accepted.connect(About.accept)
        self.buttonBox.rejected.connect(About.reject)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.info_label.setText(_translate("About", "TextLabel"))
        self.label.setText(_translate("About", "Downloader For Reddit"))
        self.link_label.setText(_translate("About", "TextLabel"))
        self.logo_label.setText(_translate("About", "TextLabel"))
        self.license_box.setHtml(_translate("About", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">Downloader For Reddit is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">Downloader For Reddit is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">You should have received a copy of the GNU General Public License along with Downloader For Reddit.  If not, see: </span><a href=\"http://www.gnu.org/licenses/\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.gnu.org/licenses/</span></a></p></body></html>"))
        self.total_downloads_label.setText(_translate("About", "Total Downloads:"))

