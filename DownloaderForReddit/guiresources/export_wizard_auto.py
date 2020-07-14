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
        self.wizardPage1 = QtWidgets.QWizardPage()
        self.wizardPage1.setObjectName("wizardPage1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.wizardPage1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.csv_export_radio = QtWidgets.QRadioButton(self.wizardPage1)
        self.csv_export_radio.setObjectName("csv_export_radio")
        self.verticalLayout.addWidget(self.csv_export_radio)
        self.json_export_radio = QtWidgets.QRadioButton(self.wizardPage1)
        self.json_export_radio.setObjectName("json_export_radio")
        self.verticalLayout.addWidget(self.json_export_radio)
        ExportWizard.addPage(self.wizardPage1)
        self.wizardPage2 = QtWidgets.QWizardPage()
        self.wizardPage2.setSubTitle("")
        self.wizardPage2.setObjectName("wizardPage2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.wizardPage2)
        self.verticalLayout_2.setSpacing(12)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.wizardPage2)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.export_complete_nested_radio = QtWidgets.QRadioButton(self.wizardPage2)
        self.export_complete_nested_radio.setObjectName("export_complete_nested_radio")
        self.verticalLayout_2.addWidget(self.export_complete_nested_radio)
        self.export_nested_name_radio = QtWidgets.QRadioButton(self.wizardPage2)
        self.export_nested_name_radio.setObjectName("export_nested_name_radio")
        self.verticalLayout_2.addWidget(self.export_nested_name_radio)
        ExportWizard.addPage(self.wizardPage2)
        self.wizardPage = QtWidgets.QWizardPage()
        self.wizardPage.setObjectName("wizardPage")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.wizardPage)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.export_path_line_edit = QtWidgets.QLineEdit(self.wizardPage)
        self.export_path_line_edit.setObjectName("export_path_line_edit")
        self.horizontalLayout.addWidget(self.export_path_line_edit)
        self.path_dialog_button = QtWidgets.QPushButton(self.wizardPage)
        self.path_dialog_button.setObjectName("path_dialog_button")
        self.horizontalLayout.addWidget(self.path_dialog_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        ExportWizard.addPage(self.wizardPage)

        self.retranslateUi(ExportWizard)
        QtCore.QMetaObject.connectSlotsByName(ExportWizard)

    def retranslateUi(self, ExportWizard):
        _translate = QtCore.QCoreApplication.translate
        ExportWizard.setWindowTitle(_translate("ExportWizard", "Export"))
        self.wizardPage1.setTitle(_translate("ExportWizard", "Export file type"))
        self.csv_export_radio.setText(_translate("ExportWizard", "CSV"))
        self.json_export_radio.setText(_translate("ExportWizard", "JSON"))
        self.wizardPage2.setTitle(_translate("ExportWizard", "Nested Object Export"))
        self.label.setText(_translate("ExportWizard", "<html><head/><body><p>How would you like nested objects?  ie: When exporting a list of users would you like the users posts to be exported with full attributes such as score, date posted, title, etc. or would you like the post to be exported as the title of the post only?</p></body></html>"))
        self.export_complete_nested_radio.setText(_translate("ExportWizard", "Export complete nested objects"))
        self.export_nested_name_radio.setText(_translate("ExportWizard", "Export names of nested objects only"))
        self.wizardPage.setTitle(_translate("ExportWizard", "Export Path"))
        self.path_dialog_button.setText(_translate("ExportWizard", "Select Path"))
