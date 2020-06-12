from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QListWidgetItem, QToolButton,
                             QInputDialog)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor

from DownloaderForReddit.guiresources.settings.quick_filter_settings_widget_auto import Ui_QuickFilterSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class QuickFilterSettingsWidget(AbstractSettingsWidget, Ui_QuickFilterSettingsWidget):

    def __init__(self):
        super().__init__()
        self.filters = None
        self.widget_item_map = {}
        self.widget_filter_map = {}

        self.filter_input_widget.quick_filter_combo.setVisible(False)

        self.name_list_widget.currentItemChanged.connect(self.select_item)
        self.filter_list_widget.setSpacing(12)
        self.filter_input_widget.export_filter.connect(self.add_filter)

        self.add_new_quick_filter_button.clicked.connect(self.add_quick_filter)

    @property
    def description(self):
        return 'These quick filters are available from a combo box in the database view dialog for quick access to ' \
               'filters that are used most often.  Multiple filters can be combined together for one quick action.'

    def load_settings(self):
        self.filters = self.settings.database_view_quick_filters
        self.name_list_widget.addItems(self.filters.keys())
        self.name_list_widget.setCurrentRow(0)

    def apply_settings(self):
        self.settings.database_view_quick_filters = self.filters

    def select_item(self, item):
        self.filter_list_widget.clear()
        for filter_item in self.filters[item.text()]:
            self.add_widget(filter_item, item.text())

    def add_widget(self, filter_item, filter_name):
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)
        main_layout.addWidget(QLabel(filter_item['model']))

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(filter_item['field']))
        filter_layout.addWidget(self.get_line())
        filter_layout.addWidget(QLabel(filter_item['operator']))
        filter_layout.addWidget(self.get_line())
        filter_layout.addWidget(QLabel(str(filter_item['value'])))

        remove_button = QToolButton()
        remove_button.setText('X')
        remove_button.clicked.connect(lambda: self.remove_filter(widget, filter_name))
        filter_layout.addWidget(remove_button)

        main_layout.addLayout(filter_layout)

        item = QListWidgetItem()
        item.setSizeHint(QSize(widget.sizeHint().width() + 25, widget.sizeHint().height() + 5))
        item.setBackground(QColor('#C8C8C8'))
        self.filter_list_widget.addItem(item)
        self.filter_list_widget.setItemWidget(item, widget)
        self.widget_item_map[widget] = item
        self.widget_filter_map[widget] = filter_item

    def get_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def remove_filter(self, widget, name):
        item = self.widget_item_map[widget]
        filter_item = self.widget_filter_map[widget]
        self.filter_list_widget.takeItem(self.filter_list_widget.row(item))
        self.filters[name].remove(filter_item)
        del self.widget_item_map[widget]
        del self.widget_filter_map[widget]

    def add_quick_filter(self):
        name, ok = QInputDialog.getText(self, 'New Quick Filter', 'Enter new quick filter name')
        if ok and name != '' and name not in self.filters.keys():
            self.filters[name] = []
            self.name_list_widget.addItem(name)
            self.name_list_widget.setCurrentRow(self.name_list_widget.count() - 1)

    def add_filter(self, filter_item_list):
        for filter_item in filter_item_list:
            filter_name = self.name_list_widget.currentItem().text()
            filter_list = self.filters[filter_name]
            filter_dict = filter_item.widget_dict
            filter_list.append(filter_dict)
            self.add_widget(filter_dict, filter_name)
