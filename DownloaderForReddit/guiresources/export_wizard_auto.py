# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Resources\ui_files\export_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExportWizard(object):
    def setupUi(self, ExportWizard):
        ExportWizard.setObjectName("ExportWizard")
        ExportWizard.resize(819, 353)
        ExportWizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.page_one = QtWidgets.QWizardPage()
        self.page_one.setObjectName("page_one")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page_one)
        self.verticalLayout.setObjectName("verticalLayout")
        self.csv_export_radio = QtWidgets.QRadioButton(self.page_one)
        self.csv_export_radio.setObjectName("csv_export_radio")
        self.verticalLayout.addWidget(self.csv_export_radio)
        self.json_export_radio = QtWidgets.QRadioButton(self.page_one)
        self.json_export_radio.setObjectName("json_export_radio")
        self.verticalLayout.addWidget(self.json_export_radio)
        ExportWizard.addPage(self.page_one)
        self.page_two = QtWidgets.QWizardPage()
        self.page_two.setSubTitle("")
        self.page_two.setObjectName("page_two")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_two)
        self.verticalLayout_2.setSpacing(12)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.page_two)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.export_complete_nested_radio = QtWidgets.QRadioButton(self.page_two)
        self.export_complete_nested_radio.setObjectName("export_complete_nested_radio")
        self.verticalLayout_2.addWidget(self.export_complete_nested_radio)
        self.export_nested_name_radio = QtWidgets.QRadioButton(self.page_two)
        self.export_nested_name_radio.setObjectName("export_nested_name_radio")
        self.verticalLayout_2.addWidget(self.export_nested_name_radio)
        ExportWizard.addPage(self.page_two)
        self.page_three = QtWidgets.QWizardPage()
        self.page_three.setObjectName("page_three")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_three)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.export_path_line_edit = QtWidgets.QLineEdit(self.page_three)
        self.export_path_line_edit.setObjectName("export_path_line_edit")
        self.horizontalLayout.addWidget(self.export_path_line_edit)
        self.path_dialog_button = QtWidgets.QPushButton(self.page_three)
        self.path_dialog_button.setObjectName("path_dialog_button")
        self.horizontalLayout.addWidget(self.path_dialog_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        ExportWizard.addPage(self.page_three)

        self.retranslateUi(ExportWizard)
        QtCore.QMetaObject.connectSlotsByName(ExportWizard)

    def retranslateUi(self, ExportWizard):
        _translate = QtCore.QCoreApplication.translate
        ExportWizard.setWindowTitle(_translate("ExportWizard", "Export"))
        self.page_one.setTitle(_translate("ExportWizard", "Export file type"))
        self.csv_export_radio.setText(_translate("ExportWizard", "CSV"))
        self.json_export_radio.setText(_translate("ExportWizard", "JSON"))
        self.page_two.setTitle(_translate("ExportWizard", "Nested Object Export"))
        self.label.setText(_translate("ExportWizard", "<html><head/><body><p>How would you like nested objects?  ie: When exporting a list of users would you like the users posts to be exported with full attributes such as score, date posted, title, etc. or would you like the post to be exported as the title of the post only?</p></body></html>"))
        self.export_complete_nested_radio.setText(_translate("ExportWizard", "Export complete nested objects"))
        self.export_nested_name_radio.setText(_translate("ExportWizard", "Export names of nested objects only"))
        self.page_three.setTitle(_translate("ExportWizard", "Export Path"))
        self.path_dialog_button.setText(_translate("ExportWizard", "Select Path"))
