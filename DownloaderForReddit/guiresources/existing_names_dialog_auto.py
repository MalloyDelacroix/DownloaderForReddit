# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\existing_names_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExistingNameDialog(object):
    def setupUi(self, ExistingNameDialog):
        ExistingNameDialog.setObjectName("ExistingNameDialog")
        ExistingNameDialog.resize(545, 610)
        self.verticalLayout = QtWidgets.QVBoxLayout(ExistingNameDialog)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(ExistingNameDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.select_all_checkbox = QtWidgets.QCheckBox(ExistingNameDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.select_all_checkbox.setFont(font)
        self.select_all_checkbox.setObjectName("select_all_checkbox")
        self.verticalLayout.addWidget(self.select_all_checkbox)
        self.name_table_widget = QtWidgets.QTableWidget(ExistingNameDialog)
        self.name_table_widget.setColumnCount(3)
        self.name_table_widget.setObjectName("name_table_widget")
        self.name_table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.name_table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.name_table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.name_table_widget.setHorizontalHeaderItem(2, item)
        self.name_table_widget.horizontalHeader().setStretchLastSection(True)
        self.name_table_widget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.name_table_widget)
        self.button_box = QtWidgets.QDialogButtonBox(ExistingNameDialog)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(ExistingNameDialog)
        self.button_box.accepted.connect(ExistingNameDialog.accept)
        self.button_box.rejected.connect(ExistingNameDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExistingNameDialog)

    def retranslateUi(self, ExistingNameDialog):
        _translate = QtCore.QCoreApplication.translate
        ExistingNameDialog.setWindowTitle(_translate("ExistingNameDialog", "Add Existing"))
        self.label.setText(_translate("ExistingNameDialog", "<html><head/><body><p>The following names already exist in the database.</p><p>How would you like to handle adding these users/subreddits?</p></body></html>"))
        self.select_all_checkbox.setText(_translate("ExistingNameDialog", "Select All"))
        self.name_table_widget.setSortingEnabled(True)
        item = self.name_table_widget.horizontalHeaderItem(0)
        item.setText(_translate("ExistingNameDialog", "Add"))
        item = self.name_table_widget.horizontalHeaderItem(1)
        item.setText(_translate("ExistingNameDialog", "Name"))
        item = self.name_table_widget.horizontalHeaderItem(2)
        item.setText(_translate("ExistingNameDialog", "List(s)"))
