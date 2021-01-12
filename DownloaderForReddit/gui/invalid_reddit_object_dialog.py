from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QHBoxLayout, QWidget, QListWidgetItem

from ..guiresources.invalid_reddit_object_dialog_auto import Ui_InvalidRedditObjectDialog


class InvalidRedditObjectDialog(QDialog, Ui_InvalidRedditObjectDialog):

    def __init__(self, invalid_ros: list):
        QDialog.__init__(self)
        self.setupUi(self)
        self.invalid_ros = invalid_ros
        self.checkbox_list = []
        self.button_box.accepted.connect(self.close)
        self.setup_decision_box()
        self.select_all_checkbox.toggled.connect(self.toggle_all)

    def setup_decision_box(self):
        for ro in self.invalid_ros:
            item = QListWidgetItem()
            widget = QWidget()
            box = QHBoxLayout()
            box.addWidget(QLabel(ro.name))
            checkbox = QCheckBox('')
            checkbox.toggled.connect(lambda x, ro=ro: setattr(ro, 'remove', x))
            self.checkbox_list.append(checkbox)
            box.addWidget(checkbox)
            box.addWidget(QLabel(ro.status))
            widget.setLayout(box)
            item.setSizeHint(widget.sizeHint())
            self.decision_list.addItem(item)
            self.decision_list.setItemWidget(item, widget)

    def toggle_all(self, checked):
        for checkbox in self.checkbox_list:
            checkbox.setChecked(checked)


class InvalidObject:

    def __init__(self, name, id_, status):
        self.name = name
        self.id = id_
        self.status = status
        self.remove = False
