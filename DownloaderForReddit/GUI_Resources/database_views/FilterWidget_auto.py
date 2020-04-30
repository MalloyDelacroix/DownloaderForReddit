# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FilterWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FilterWidget(object):
    def setupUi(self, FilterWidget):
        FilterWidget.setObjectName("FilterWidget")
        FilterWidget.resize(1700, 190)
        self.horizontalLayout = QtWidgets.QHBoxLayout(FilterWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(FilterWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.field_combo = QtWidgets.QComboBox(FilterWidget)
        self.field_combo.setMinimumSize(QtCore.QSize(300, 0))
        self.field_combo.setObjectName("field_combo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.field_combo)
        self.label_2 = QtWidgets.QLabel(FilterWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.operator_combo = QtWidgets.QComboBox(FilterWidget)
        self.operator_combo.setObjectName("operator_combo")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.operator_combo)
        self.label_3 = QtWidgets.QLabel(FilterWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.value_layout = QtWidgets.QVBoxLayout()
        self.value_layout.setObjectName("value_layout")
        self.value_line_edit = QtWidgets.QLineEdit(FilterWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.value_line_edit.sizePolicy().hasHeightForWidth())
        self.value_line_edit.setSizePolicy(sizePolicy)
        self.value_line_edit.setObjectName("value_line_edit")
        self.value_layout.addWidget(self.value_line_edit)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.value_layout)
        self.label_4 = QtWidgets.QLabel(FilterWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label_4)
        self.horizontalLayout.addLayout(self.formLayout)
        self.filter_box_list_widget = QtWidgets.QListWidget(FilterWidget)
        self.filter_box_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.filter_box_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.filter_box_list_widget.setMovement(QtWidgets.QListView.Snap)
        self.filter_box_list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.filter_box_list_widget.setObjectName("filter_box_list_widget")
        self.horizontalLayout.addWidget(self.filter_box_list_widget)

        self.retranslateUi(FilterWidget)
        QtCore.QMetaObject.connectSlotsByName(FilterWidget)

    def retranslateUi(self, FilterWidget):
        _translate = QtCore.QCoreApplication.translate
        FilterWidget.setWindowTitle(_translate("FilterWidget", "Filter"))
        self.label.setText(_translate("FilterWidget", "Field:"))
        self.label_2.setText(_translate("FilterWidget", "Operator:"))
        self.label_3.setText(_translate("FilterWidget", "Value:"))
        self.label_4.setText(_translate("FilterWidget", "Filter"))

