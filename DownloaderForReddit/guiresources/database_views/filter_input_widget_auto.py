# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Kyle/PycharmProjects/DownloaderForReddit/Resources/ui_files//database_views/filter_input_widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FilterInputWidget(object):
    def setupUi(self, FilterInputWidget):
        FilterInputWidget.setObjectName("FilterInputWidget")
        FilterInputWidget.resize(479, 255)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterInputWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.form_layout.setObjectName("form_layout")
        self.title_label = QtWidgets.QLabel(FilterInputWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setObjectName("title_label")
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.title_label)
        self.label_5 = QtWidgets.QLabel(FilterInputWidget)
        self.label_5.setObjectName("label_5")
        self.form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.model_combo = QtWidgets.QComboBox(FilterInputWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_combo.sizePolicy().hasHeightForWidth())
        self.model_combo.setSizePolicy(sizePolicy)
        self.model_combo.setObjectName("model_combo")
        self.form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.model_combo)
        self.label = QtWidgets.QLabel(FilterInputWidget)
        self.label.setObjectName("label")
        self.form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.field_combo = QtWidgets.QComboBox(FilterInputWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.field_combo.sizePolicy().hasHeightForWidth())
        self.field_combo.setSizePolicy(sizePolicy)
        self.field_combo.setMinimumSize(QtCore.QSize(300, 0))
        self.field_combo.setObjectName("field_combo")
        self.form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.field_combo)
        self.label_2 = QtWidgets.QLabel(FilterInputWidget)
        self.label_2.setObjectName("label_2")
        self.form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.operator_combo = QtWidgets.QComboBox(FilterInputWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.operator_combo.sizePolicy().hasHeightForWidth())
        self.operator_combo.setSizePolicy(sizePolicy)
        self.operator_combo.setObjectName("operator_combo")
        self.form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.operator_combo)
        self.label_3 = QtWidgets.QLabel(FilterInputWidget)
        self.label_3.setObjectName("label_3")
        self.form_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.value_layout = QtWidgets.QVBoxLayout()
        self.value_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.value_layout.setObjectName("value_layout")
        self.form_layout.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.value_layout)
        self.add_filter_button = QtWidgets.QPushButton(FilterInputWidget)
        self.add_filter_button.setObjectName("add_filter_button")
        self.form_layout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.add_filter_button)
        self.quick_filter_combo = QtWidgets.QComboBox(FilterInputWidget)
        self.quick_filter_combo.setObjectName("quick_filter_combo")
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.quick_filter_combo)
        self.verticalLayout.addLayout(self.form_layout)

        self.retranslateUi(FilterInputWidget)
        QtCore.QMetaObject.connectSlotsByName(FilterInputWidget)

    def retranslateUi(self, FilterInputWidget):
        _translate = QtCore.QCoreApplication.translate
        FilterInputWidget.setWindowTitle(_translate("FilterInputWidget", "Filter Input"))
        self.title_label.setText(_translate("FilterInputWidget", "Filter"))
        self.label_5.setText(_translate("FilterInputWidget", "Model:"))
        self.label.setText(_translate("FilterInputWidget", "Field:"))
        self.label_2.setText(_translate("FilterInputWidget", "Operator:"))
        self.label_3.setText(_translate("FilterInputWidget", "Value:"))
        self.add_filter_button.setText(_translate("FilterInputWidget", "Add Filter"))
