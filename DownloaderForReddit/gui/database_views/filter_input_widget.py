from PyQt5.QtWidgets import (QWidget, QLineEdit, QSpinBox, QComboBox, QDateTimeEdit, QSizePolicy, QMenu, QInputDialog,
                             QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from sqlalchemy import Integer, String, DateTime, Enum, Boolean

from DownloaderForReddit.guiresources.database_views.filter_input_widget_auto import Ui_FilterInputWidget
from DownloaderForReddit.database.filters import (DownloadSessionFilter, RedditObjectFilter, PostFilter, ContentFilter,
                                                  CommentFilter)
from DownloaderForReddit.utils import injector
from .filter_item import FilterItem


class FilterInputWidget(QWidget, Ui_FilterInputWidget):

    export_filter = pyqtSignal(object)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.settings_manager = injector.get_settings_manager()
        self.filter_model_map = {
            'DOWNLOAD_SESSION': DownloadSessionFilter,
            'REDDIT_OBJECT': RedditObjectFilter,
            'POST': PostFilter,
            'CONTENT': ContentFilter,
            'COMMENT': CommentFilter
        }

        self.field_type_map = {
            Boolean: self.get_boolean_field,
            Integer: self.get_integer_field,
            String: self.get_string_field,
            DateTime: self.get_datetime_field
        }

        self.value_field = None

        self.add_filter_button.clicked.connect(self.add_filter)
        self.model_combo.currentIndexChanged.connect(self.set_fields)

        self.model_combo.addItem('Download Session', 'DOWNLOAD_SESSION')
        self.model_combo.addItem('Reddit Object', 'REDDIT_OBJECT')
        self.model_combo.addItem('Post', 'POST')
        self.model_combo.addItem('Content', 'CONTENT')
        self.model_combo.addItem('Comment', 'COMMENT')

        operators = [('Equal To', 'eq'), ('Not Equal', 'not'), ('<', 'lt'), ('<=', 'lte'), ('>', 'gt'), ('>=', 'gte'),
                     ('In', 'in'), ('Like', 'like'), ('Contains', 'contains')]
        for x in operators:
            self.operator_combo.addItem(x[0], x[1])

        self.set_fields()
        self.field_combo.currentIndexChanged.connect(self.set_value_field)
        self.set_value_field()

        self.quick_filter_label.clicked.connect(self.quick_filters_menu)
        self.quick_filter_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.quick_filter_label.customContextMenuRequested.connect(self.quick_filters_menu)

    @property
    def current_model(self):
        return self.model_combo.currentData(Qt.UserRole)

    @property
    def current_field(self):
        return self.field_combo.currentData(Qt.UserRole)

    @property
    def current_operator(self):
        return self.operator_combo.currentData(Qt.UserRole)

    def set_fields(self):
        self.field_combo.clear()
        f = self.filter_model_map[self.current_model]
        for field in f.get_filter_fields():
            self.field_combo.addItem(field.replace('_', ' ').title(), field)

    def set_value_field(self):
        current_field = self.current_field
        if current_field is not None:
            f = self.filter_model_map[self.current_model]()
            filed_type = f.get_type(current_field)
            if filed_type == Enum:
                field = self.get_choice_field(choices=f.get_choices(current_field))
            else:
                field = self.field_type_map[filed_type]()
            if not isinstance(field, type(self.value_field)):
                try:
                    self.value_layout.removeWidget(self.value_field)
                    self.value_field.deleteLater()
                except AttributeError:
                    pass
                self.value_field = field
                self.value_layout.addWidget(self.value_field)

    def get_value(self):
        t = type(self.value_field)
        if t == QComboBox:
            return self.value_field.currentData(Qt.UserRole)
        elif t == QLineEdit:
            return self.value_field.text()
        elif t == QSpinBox:
            return self.value_field.value()

    def quick_filters_menu(self):
        quick_filters = self.settings_manager.database_view_quick_filters
        menu = QMenu()
        for key, value in quick_filters.items():
            menu.addAction(key.replace('_', ' ').title(),
                           lambda filter_list=value: self.handle_quick_filter(filter_list))
        menu.addSeparator()
        make_new_quick_filter = menu.addAction('Make Current Quick Filter', self.make_current_quick_filter)
        make_new_quick_filter.setToolTip('Makes the current selection of filtering options into a quick filter')
        menu.exec_(QCursor.pos())

    def handle_quick_filter(self, filter_list):
        for filter_item in filter_list:
            f = FilterItem(**filter_item)
            self.add_filter(f)

    def make_current_quick_filter(self):
        filter_name, ok = QInputDialog.getText(self, 'Quick Filter Name', 'Enter name for quick filter:')
        if ok and filter_name != '' and not filter_name in self.settings_manager.database_view_quick_filters:
            filter_item = {'model': self.current_model, 'attribute': self.current_field,
                           'operator': self.current_operator, 'value': self.get_value()}
            for filter_list in self.settings_manager.database_view_quick_filters.values():
                if filter_item in filter_list:
                    return
            self.settings_manager[filter_name] = filter_item

    def add_filter(self, filter_item=None):
        if type(filter_item) != FilterItem:
            filter_item = self.create_filter()
        self.export_filter.emit(filter_item)

    def create_filter(self):
        return FilterItem(self.current_model, self.current_field, self.current_operator, self.get_value())

    def get_boolean_field(self):
        combo = QComboBox()
        combo.addItem('True', True)
        combo.addItem('False', False)
        return combo

    def get_integer_field(self):
        return QSpinBox()

    def get_string_field(self):
        x = QLineEdit()
        x.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        return x

    def get_choice_field(self, choices):
        combo = QComboBox()
        for x in choices:
            combo.addItem(x)
        return combo

    def get_datetime_field(self):
        return QDateTimeEdit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.add_filter()
