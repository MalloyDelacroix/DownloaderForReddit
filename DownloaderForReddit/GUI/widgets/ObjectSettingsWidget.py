from datetime import datetime
from PyQt5.QtWidgets import QWidget, QMenu, QApplication, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ...GUI_Resources.widgets.ObjectSettingsWidget_auto import Ui_ObjectSettingsWidget
from ...Database.ModelEnums import *
from ...Utils import TokenParser


class ObjectSettingsWidget(QWidget, Ui_ObjectSettingsWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.setup_widgets()
        self.connect_edit_widgets()
        self.selected_objects = []

    def set_objects(self, object_list):
        if object_list:
            self.selected_objects = object_list
            self.sync_widgets_to_object()

    def setup_widgets(self):
        for value in LimitOperator:
            self.score_limit_operator_combo.addItem(value.display_name, value)
            self.comment_score_operator_combo.addItem(value.display_name, value)
        self.self_post_file_format_combo.addItem('.txt', 'txt')
        self.self_post_file_format_combo.addItem('.html', 'html')
        for value in NsfwFilter:
            self.nsfw_filter_combo.addItem(value.display_name, value)
        for value in PostSortMethod:
            self.post_sort_combo.addItem(value.display_name, value)
        for value in CommentDownload:
            self.comment_extract_combo.addItem(value.display_name, value)
            self.comment_download_combo.addItem(value.display_name, value)
            self.comment_content_download_combo.addItem(value.display_name, value)
        for value in CommentSortMethod:
            self.comment_sort_combo.addItem(value.display_name, value)

        self.post_download_naming_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.post_download_naming_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.post_download_naming_line_edit))
        self.post_download_naming_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.post_download_naming_line_edit))

        self.post_save_path_structure_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.post_save_path_structure_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.post_save_path_structure_line_edit))
        self.post_save_structure_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.post_save_path_structure_line_edit))

        self.comment_download_naming_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.comment_download_naming_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.comment_download_naming_line_edit))
        self.comment_download_naming_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.comment_download_naming_line_edit))

        self.comment_save_path_structure_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.comment_save_path_structure_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.comment_save_path_structure_line_edit))
        self.comment_save_structure_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.comment_save_path_structure_line_edit))

        self.post_limit_max_button.clicked.connect(
            lambda: self.post_limit_spinbox.setValue(self.post_limit_spinbox.maximum()))
        self.comment_limit_max_button.clicked.connect(
            lambda: self.comment_limit_spinbox.setValue(self.comment_limit_spinbox.maximum()))

    def connect_edit_widgets(self):
        self.setup_checkbox(self.lock_settings_checkbox, 'lock_settings')
        self.post_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('post_limit', x))
        self.score_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('post_score_limit', x))
        self.score_limit_operator_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('post_score_limit_operator', self.score_limit_operator_combo.itemData(x))
        )
        self.date_limit_checkbox.stateChanged.connect(self.date_limit_checkbox_toggled)
        self.date_limit_edit.dateTimeChanged.connect(self.set_date_limit_from_edit)
        self.setup_checkbox(self.avoid_duplicates_checkbox, 'avoid_duplicates')
        self.setup_checkbox(self.extract_self_post_content_checkbox, 'extract_self_post_links')
        self.setup_checkbox(self.download_self_post_text_checkbox, 'download_self_post_text')
        self.self_post_file_format_combo.currentIndexChanged.connect(
            lambda: self.set_object_value('self_post_file_format',
                                          self.self_post_file_format_combo.currentText().strip('.')))
        self.setup_checkbox(self.download_videos_checkbox, 'download_videos')
        self.setup_checkbox(self.download_images_checkbox, 'download_images')
        self.nsfw_filter_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('download_nsfw', self.nsfw_filter_combo.itemData(x))
        )
        self.post_sort_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('post_sort_method', self.post_sort_combo.itemData(x))
        )
        self.post_download_naming_line_edit.editingFinished.connect(
            lambda: self.set_object_value('post_download_naming_method', self.post_download_naming_line_edit.text()))
        self.post_save_path_structure_line_edit.editingFinished.connect(
            lambda: self.set_object_value('post_save_structure', self.post_save_path_structure_line_edit.text()))
        self.comment_extract_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('extract_comments', self.comment_extract_combo.itemData(x))
        )
        self.comment_download_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('download_comments', self.comment_download_combo.itemData(x))
        )
        self.comment_content_download_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('download_comment_content', self.comment_content_download_combo.itemData(x))
        )
        self.comment_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('comment_limit', x))
        self.comment_score_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('comment_score_limit', x))
        self.comment_score_operator_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('comment_score_limit_operator',
                                            self.comment_score_operator_combo.itemData(x))
        )
        self.comment_sort_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('comment_sort_method', self.comment_sort_combo.itemData(x))
        )
        self.comment_download_naming_line_edit.editingFinished.connect(
            lambda: self.set_object_value('comment_naming_method', self.comment_download_naming_line_edit.text())
        )
        self.comment_save_path_structure_line_edit.editingFinished.connect(
            lambda: self.set_object_value('comment_save_structure', self.comment_save_path_structure_line_edit.text())
        )

    def setup_checkbox(self, checkbox, attribute):
        checkbox.stateChanged.connect(lambda: self.set_object_value(attribute, checkbox.isChecked()))

    def date_limit_checkbox_toggled(self):
        checked = self.date_limit_checkbox.isChecked()
        self.date_limit_edit.setDisabled(not checked)
        if checked:
            self.set_date_limit_from_edit()
        else:
            self.set_object_value('date_limit', None)

    def set_date_limit_from_edit(self):
        epoch = self.date_limit_edit.dateTime().toSecsSinceEpoch()
        self.set_object_value('date_limit', datetime.fromtimestamp(epoch))

    def set_object_value(self, attr, value):
        for obj in self.selected_objects:
            setattr(obj, attr, value)
            if obj.object_type == 'REDDIT_OBJECT_LIST':
                for ro in obj.reddit_objects:
                    if not ro.lock_settings:
                        setattr(ro, attr, value)

    def path_token_context_menu(self, line_edit):
        menu = QMenu()
        for key in TokenParser.token_dict.keys():
            menu.addAction(key.replace('_', ' ').title(), lambda token=key: self.insert_token(line_edit, token))
        menu.exec_(QCursor.pos())

    def insert_token(self, line_edit, token):
        if line_edit.hasSelectedText():
            line_edit.del_()
        line_edit.insert(f'%[{token}]')

    def sync_widgets_to_object(self):
        self.sync_optional()
        self.sync_spin_box(self.post_limit_spinbox, 'post_limit')
        self.sync_spin_box(self.score_limit_spinbox, 'post_score_limit')
        self.sync_combo(self.score_limit_operator_combo, 'post_score_limit_operator')
        self.sync_checkbox(self.avoid_duplicates_checkbox, 'avoid_duplicates')
        self.sync_checkbox(self.extract_self_post_content_checkbox, 'extract_self_post_links')
        self.sync_checkbox(self.download_self_post_text_checkbox, 'download_self_post_text')
        self.sync_combo(self.self_post_file_format_combo, 'self_post_file_format')
        self.sync_checkbox(self.download_videos_checkbox, 'download_videos')
        self.sync_checkbox(self.download_images_checkbox, 'download_images')
        self.sync_checkbox(self.download_gifs_checkbox, 'download_gifs')
        self.sync_combo(self.nsfw_filter_combo, 'download_nsfw')
        self.sync_combo(self.post_sort_combo, 'post_sort_method')
        self.sync_line_edit(self.post_download_naming_line_edit, 'post_download_naming_method')
        self.sync_line_edit(self.post_save_path_structure_line_edit, 'post_save_structure')
        self.sync_combo(self.comment_extract_combo, 'extract_comments')
        self.sync_combo(self.comment_download_combo, 'download_comments')
        self.sync_combo(self.comment_content_download_combo, 'download_comment_content')
        self.sync_spin_box(self.comment_score_limit_spinbox, 'comment_limit')
        self.sync_spin_box(self.comment_score_limit_spinbox, 'comment_score_limit')
        self.sync_combo(self.comment_score_operator_combo, 'comment_score_limit_operator')
        self.sync_combo(self.comment_sort_combo, 'comment_sort_method')
        self.sync_line_edit(self.comment_download_naming_line_edit, 'comment_naming_method')
        self.sync_line_edit(self.comment_save_path_structure_line_edit, 'comment_save_structure')

    def sync_optional(self):
        try:
            self.sync_checkbox(self.lock_settings_checkbox, 'lock_settings')
            self.sync_checkbox(self.enable_download_checkbox, 'download_enabled')
            visibility = True
        except (AttributeError, TypeError):
            visibility = False
        self.lock_settings_checkbox.setVisible(visibility)
        self.enable_download_checkbox.setVisible(visibility)

    def sync_checkbox(self, checkbox, attr):
        value = self.get_value(attr)
        if value is not None:
            if value:
                checkbox.setCheckState(2)
            else:
                checkbox.setCheckState(0)
        else:
            checkbox.setCheckState(1)

    def sync_combo(self, combo, attr):
        value = self.get_value(attr)
        if value is not None:
            combo.setCurrentIndex(combo.findData(value))
        else:
            combo.setCurrentIndex(-1)

    def sync_spin_box(self, spin_box, attr):
        value = self.get_value(attr)
        if value is not None:
            spin_box.setValue(value)
        else:
            spin_box.lineEdit().setText('-')

    def sync_date_edit(self, date_edit, attr):
        value = self.get_value(attr)
        if value is not None:
            date_edit.setDateTime(value)
        else:
            date_edit.lineEdit().setText('-')

    def sync_line_edit(self, line_edit, attr):
        value = self.get_value(attr)
        if value is None:
            value = ''
        line_edit.setText(value)

    def get_value(self, attr):
        value = getattr(self.selected_objects[0], attr)
        if len(self.selected_objects) == 1 or all(getattr(x, attr) == value for x in self.selected_objects):
            return value
        return None

    def sync_date_limits(self):
        date_limit = getattr(self.selected_objects[0], 'date_limit')
        if all(getattr(x, 'date_limit') == date_limit for x in self.selected_objects):
            self.date_limit_checkbox.setChecked(date_limit is not None)
            self.date_limit_edit.setDisabled(date_limit is None)
            if date_limit is not None:
                self.date_limit_edit.setDateTime(date_limit)
            else:
                self.set_absolute_date_limit()
        else:
            self.date_limit_checkbox.setChecked(False)
            self.date_limit_edit.setDisabled(False)
            self.date_limit_edit.lineEdit().setText('-')

    def set_absolute_date_limit(self):
        try:
            absolute_date_limit = getattr(self.selected_objects[0], 'absolute_date_limit')
            if all(getattr(x, 'absolute_date_limit') == absolute_date_limit for x in self.selected_objects):
                self.date_limit_edit.setDateTime(absolute_date_limit)
            else:
                self.date_limit_edit.lineEdit().setText('-')
            visible = True
        except TypeError:
            visible = False
        self.date_limit_edit.setVisible(visible)
        self.date_limit_checkbox.setVisible(visible)

    def setup_for_master_list(self):
        post_naming_button = QPushButton('User')

    def make_ro_toggle_button(self):
        button = QPushButton('User')
        button.setCheckable(True)
