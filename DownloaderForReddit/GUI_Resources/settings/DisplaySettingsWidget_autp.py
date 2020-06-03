# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DisplaySettingsWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DispalySettingsWidget(object):
    def setupUi(self, DispalySettingsWidget):
        DispalySettingsWidget.setObjectName("DispalySettingsWidget")
        DispalySettingsWidget.resize(906, 709)
        self.verticalLayout = QtWidgets.QVBoxLayout(DispalySettingsWidget)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setVerticalSpacing(12)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DispalySettingsWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.short_title_length_spin_box = QtWidgets.QSpinBox(DispalySettingsWidget)
        self.short_title_length_spin_box.setMinimumSize(QtCore.QSize(100, 0))
        self.short_title_length_spin_box.setObjectName("short_title_length_spin_box")
        self.horizontalLayout.addWidget(self.short_title_length_spin_box)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.tooltip_groupbox = QtWidgets.QGroupBox(DispalySettingsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tooltip_groupbox.sizePolicy().hasHeightForWidth())
        self.tooltip_groupbox.setSizePolicy(sizePolicy)
        self.tooltip_groupbox.setObjectName("tooltip_groupbox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tooltip_groupbox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout.addWidget(self.tooltip_groupbox)

        self.retranslateUi(DispalySettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(DispalySettingsWidget)

    def retranslateUi(self, DispalySettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        DispalySettingsWidget.setWindowTitle(_translate("DispalySettingsWidget", "Display Settings"))
        self.label.setToolTip(_translate("DispalySettingsWidget", "<html><head/><body><p>In most displays titles are shortened in order to display better. This dictates how many characters titles will be shortened to (set to &quot;0&quot; if you don\'t want titles shortened)</p></body></html>"))
        self.label.setText(_translate("DispalySettingsWidget", "Short title char length:"))
        self.tooltip_groupbox.setTitle(_translate("DispalySettingsWidget", "User/Subreddit Tooltip Display"))
