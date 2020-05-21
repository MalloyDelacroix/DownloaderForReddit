from PyQt5.QtWidgets import (QWidget, QLabel, QToolButton, QHBoxLayout, QVBoxLayout, QListWidgetItem, QFrame, QLineEdit,
                             QSpinBox, QComboBox, QDateTimeEdit, QSizePolicy, QListView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from sqlalchemy import Integer, String, DateTime, Enum, Boolean

from DownloaderForReddit.GUI_Resources.database_views.FilterWidget_auto import Ui_FilterWidget
from DownloaderForReddit.Database.Filters import (DownloadSessionFilter, RedditObjectFilter, PostFilter, ContentFilter,
                                                  CommentFilter)


class FilterWidget(QWidget, Ui_FilterWidget):
    filter_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.active = False
        self.filters = {}
        self.list_item_map = {}
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
        self.filter_box_list_widget.setSpacing(12)
        self.filter_box_list_widget.setResizeMode(QListView.Adjust)

        self.add_filter_button.clicked.connect(self.add_filter)
        self.model_combo.currentIndexChanged.connect(self.set_fields)

        self.model_combo.addItem('Download Session', 'DOWNLOAD_SESSION')
        self.model_combo.addItem('Reddit Object', 'REDDIT_OBJECT')
        self.model_combo.addItem('Post', 'POST')
        self.model_combo.addItem('Content', 'CONTENT')
        self.model_combo.addItem('Comment', 'COMMENT')

        operators = [('Equal To', 'eq'), ('<', 'lt'), ('<=', 'lte'), ('>', 'gt'), ('>=', 'gte'), ('In', 'in'),
                     ('Like', 'like'), ('Contains', 'contains')]
        for x in operators:
            self.operator_combo.addItem(x[0], x[1])

        self.set_fields()
        self.field_combo.currentIndexChanged.connect(self.set_value_field)
        self.set_value_field()

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

    def filter(self, model_name):
        return self.filter_download_filters(model_name)

    def filter_download_filters(self, filter_name):
        return [x.filter_tuple for x in filter(lambda x: x.model == filter_name, self.filters.values())]

    def add_filter(self):
        filter_tuple = self.create_filter()
        widget = self.create_widget()
        self.filters[widget] = filter_tuple
        self.add_widget_to_list(widget)
        self.filter_changed.emit(self.current_model)
        self.value_field.clear()

    def add_widget_to_list(self, widget):
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setBackground(QColor('#C8C8C8'))
        self.filter_box_list_widget.addItem(item)
        self.filter_box_list_widget.setItemWidget(item, widget)
        self.list_item_map[widget] = item

    def create_filter(self):
        return FilterItem(self.current_model, self.current_field, self.current_operator, self.get_value())

    def create_widget(self):
        filter_item_widget = QWidget()

        model_label = QLabel(self.model_combo.currentText())
        field_label = QLabel(self.field_combo.currentText())
        operator_label = QLabel(self.current_operator)
        # space added to this label text because it's the only way I could get it to stop cutting off the end of text
        value_label = QLabel(str(self.get_value()) + '   ')

        close_button = QToolButton()
        close_button.setText('X')
        close_button.clicked.connect(lambda: self.remove_filter(filter_item_widget))

        v_layout = QVBoxLayout()
        title_layout = QHBoxLayout()
        title_layout.addWidget(model_label)
        title_layout.addWidget(close_button)

        h_layout = QHBoxLayout()
        h_layout.addWidget(field_label)
        h_layout.addWidget(self.get_line())
        h_layout.addWidget(operator_label)
        h_layout.addWidget(self.get_line())
        h_layout.addWidget(value_label)

        v_layout.addItem(title_layout)
        v_layout.addItem(h_layout)
        h_layout.setSpacing(5)
        v_layout.setSpacing(2)

        filter_item_widget.setLayout(v_layout)
        return filter_item_widget

    def get_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def remove_filter(self, widget):
        del self.filters[widget]
        item = self.list_item_map[widget]
        row = self.filter_box_list_widget.row(item)
        self.filter_box_list_widget.takeItem(row)
        self.filter_changed.emit(self.current_model)

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
        self.add_filter()


class FilterItem:

    def __init__(self, model, field, operator, value):
        self.model = model
        self.field = field
        self.operator = operator
        self.value = value

    @property
    def filter_tuple(self):
        return self.field, self.operator, self.value
