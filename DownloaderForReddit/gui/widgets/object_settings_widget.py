import os
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QMenu, QButtonGroup, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ...guiresources.widgets.object_settings_widget_auto import Ui_ObjectSettingsWidget
from ...database.models import User, Subreddit, Post
from ...database.model_enums import *
from ...utils import TokenParser, injector
from ...core import const


class ObjectSettingsWidget(QWidget, Ui_ObjectSettingsWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.settings_manager = injector.get_settings_manager()
        self.setup_widgets()
        self.connect_edit_widgets()
        self.selected_objects = []

        self.user = User(
            id=45,
            name='UserName',
        )
        self.subreddit = Subreddit(
            id=79,
            name='SubredditName'
        )
        self.post = Post(
            id=42,
            title='Example_Post_Title',
            date_posted=datetime.now(),
            reddit_id='23sdf9lksdf',
            domain='i.imgur.com',
            extraction_date=datetime.now(),
            author=self.user,
            subreddit=self.subreddit,
            score=2573
        )

        date_limit_group = QButtonGroup(self)
        date_limit_group.addButton(self.absolute_date_limit_radio)
        date_limit_group.addButton(self.custom_date_limit_radio)

        date_lock_group = QButtonGroup(self)
        date_lock_group.addButton(self.update_custom_date_limit_radio)
        date_lock_group.addButton(self.do_not_update_custom_date_limit_radio)

    @property
    def object_type(self):
        try:
            return self.selected_objects[0].object_type
        except (IndexError, AttributeError):
            return None

    def set_objects(self, object_list):
        if object_list:
            self.selected_objects = object_list
            self.sync_widgets_to_object()
            self.sync_sort_methods(self.object_type)

    def sync_sort_methods(self, object_type):
        pos = self.post_sort_combo.findData(PostSortMethod.RISING, Qt.UserRole)
        if object_type == 'SUBREDDIT':
            if pos < 0:
                self.post_sort_combo.insertItem(2, 'RISING', PostSortMethod.RISING)
        else:
            if pos >= 0:
                self.post_sort_combo.removeItem(pos)

    def setup_widgets(self):
        for value in LimitOperator:
            self.score_limit_operator_combo.addItem(value.display_name, value)
            self.comment_score_operator_combo.addItem(value.display_name, value)
        for ext in ['txt', 'html']:
            self.self_post_file_format_combo.addItem(f'.{ext}', ext)
            self.comment_file_format_combo.addItem(f'.{ext}', ext)
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
        self.choose_custom_post_save_path_button.clicked.connect(
            lambda: self.custom_post_save_path_line_edit.setText(self.choose_file_path())
        )

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
        self.choose_custom_comment_save_path_button.clicked.connect(
            lambda: self.custom_comment_save_path_line_edit.setText(self.choose_file_path())
        )

        self.post_limit_max_button.clicked.connect(
            lambda: self.post_limit_spinbox.setValue(self.post_limit_spinbox.maximum()))
        self.comment_limit_max_button.clicked.connect(
            lambda: self.comment_limit_spinbox.setValue(self.comment_limit_spinbox.maximum()))
        self.comment_depth_max_button.clicked.connect(
            lambda: self.comment_depth_spinbox.setValue(self.comment_depth_spinbox.maximum()))
        self.comment_reply_max_button.clicked.connect(
            lambda: self.comment_reply_limit_spinbox.setValue(self.comment_reply_limit_spinbox.maximum()))

    def connect_edit_widgets(self):
        self.setup_checkbox(self.lock_settings_checkbox, 'lock_settings')
        self.setup_checkbox(self.enable_download_checkbox, 'download_enabled')
        self.post_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('post_limit', x))
        self.score_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('post_score_limit', x))
        self.score_limit_operator_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('post_score_limit_operator', self.score_limit_operator_combo.itemData(x))
        )
        self.limit_date_checkbox.stateChanged.connect(self.limit_date_checkbox_toggled)
        self.custom_date_limit_radio.toggled.connect(self.custom_date_limit_toggled)
        self.custom_date_limit_edit.dateTimeChanged.connect(self.set_date_limit_from_edit)
        self.update_custom_date_limit_radio.toggled.connect(lambda x: self.set_object_value('update_date_limit', x))
        self.setup_checkbox(self.avoid_duplicates_checkbox, 'avoid_duplicates')
        self.setup_checkbox(self.extract_self_post_content_checkbox, 'extract_self_post_links')
        self.setup_checkbox(self.download_self_post_text_checkbox, 'download_self_post_text')
        self.self_post_file_format_combo.currentIndexChanged.connect(
            lambda: self.set_object_value('self_post_file_format',
                                          self.self_post_file_format_combo.currentData(Qt.UserRole))
        )
        self.setup_checkbox(self.download_videos_checkbox, 'download_videos')
        self.setup_checkbox(self.download_images_checkbox, 'download_images')
        self.setup_checkbox(self.download_gifs_checkbox, 'download_gifs')
        self.nsfw_filter_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('download_nsfw', self.nsfw_filter_combo.itemData(x))
        )
        self.post_sort_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('post_sort_method', self.post_sort_combo.itemData(x))
        )
        self.post_download_naming_line_edit.textChanged.connect(self.sync_post_path_example)
        self.post_download_naming_line_edit.textChanged.connect(
            lambda: self.set_object_value('post_download_naming_method', self.post_download_naming_line_edit.text())
        )
        self.post_save_path_structure_line_edit.textChanged.connect(self.sync_post_path_example)
        self.post_save_path_structure_line_edit.textChanged.connect(
            lambda: self.set_object_value('post_save_structure', self.post_save_path_structure_line_edit.text())
        )
        self.custom_post_save_path_line_edit.textChanged.connect(self.sync_post_path_example)
        self.custom_post_save_path_line_edit.textChanged.connect(
            lambda: self.set_object_value('custom_post_save_path', self.custom_post_save_path_line_edit.text(),
                                          set_null=True)
        )

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
        self.comment_depth_spinbox.valueChanged.connect(lambda x: self.set_object_value('comment_depth', x))
        self.comment_reply_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('comment_reply_limit', x))
        self.comment_score_limit_spinbox.valueChanged.connect(lambda x: self.set_object_value('comment_score_limit', x))
        self.comment_score_operator_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('comment_score_limit_operator',
                                            self.comment_score_operator_combo.itemData(x))
        )
        self.comment_sort_combo.currentIndexChanged.connect(
            lambda x: self.set_object_value('comment_sort_method', self.comment_sort_combo.itemData(x))
        )
        self.comment_file_format_combo.currentIndexChanged.connect(
            lambda: self.set_object_value('comment_file_format',
                                          self.comment_file_format_combo.currentData(Qt.UserRole))
        )
        self.comment_download_naming_line_edit.textChanged.connect(self.sync_comment_path_example)
        self.comment_download_naming_line_edit.textChanged.connect(
            lambda: self.set_object_value('comment_naming_method', self.comment_download_naming_line_edit.text())
        )
        self.comment_save_path_structure_line_edit.textChanged.connect(self.sync_comment_path_example)
        self.comment_save_path_structure_line_edit.textChanged.connect(
            lambda: self.set_object_value('comment_save_structure', self.comment_save_path_structure_line_edit.text())
        )
        self.custom_comment_save_path_line_edit.textChanged.connect(self.sync_comment_path_example)
        self.custom_comment_save_path_line_edit.textChanged.connect(
            lambda: self.set_object_value('custom_comment_save_path', self.custom_comment_save_path_line_edit.text(),
                                          set_null=True)
        )

    def setup_checkbox(self, checkbox, attribute):
        checkbox.stateChanged.connect(lambda: self.set_object_value(attribute, checkbox.isChecked()))

    def limit_date_checkbox_toggled(self):
        checked = self.limit_date_checkbox.isChecked()
        self.absolute_date_limit_radio.setEnabled(checked)
        self.custom_date_limit_radio.setEnabled(checked)
        self.custom_date_limit_edit.setEnabled(checked)
        self.update_custom_date_limit_radio.setEnabled(checked)
        self.do_not_update_custom_date_limit_radio.setEnabled(checked)
        if not checked:
            self.set_object_value('date_limit', datetime.fromtimestamp(const.FIRST_POST_EPOCH - 2000))
        else:
            self.custom_date_limit_edit.setDateTime(datetime.fromtimestamp(const.FIRST_POST_EPOCH))

    def custom_date_limit_toggled(self):
        checked = self.custom_date_limit_radio.isChecked() and self.limit_date_checkbox.isChecked()
        self.custom_date_limit_edit.setEnabled(checked)
        self.update_custom_date_limit_radio.setEnabled(checked)
        self.do_not_update_custom_date_limit_radio.setEnabled(checked)
        if checked:
            self.set_date_limit_from_edit()
        else:
            self.set_object_value('date_limit', None)

    def set_date_limit_from_edit(self):
        epoch = self.custom_date_limit_edit.dateTime().toSecsSinceEpoch()
        self.set_object_value('date_limit', datetime.fromtimestamp(epoch))

    def set_object_value(self, attr, value, set_null=False):
        for obj in self.selected_objects:
            if set_null and value == '':
                value = None
            setattr(obj, attr, value)
            if obj.object_type == 'REDDIT_OBJECT_LIST':
                obj.updated = True

    def path_token_context_menu(self, line_edit):
        menu = QMenu()
        for key in TokenParser.token_dict.keys():
            menu.addAction(key.replace('_', ' ').title(), lambda token=key: self.insert_token(line_edit, token))
        menu.exec_(QCursor.pos())

    def insert_token(self, line_edit, token):
        if line_edit.hasSelectedText():
            line_edit.del_()
        line_edit.insert(f'%[{token}]')

    def sync_post_path_example(self):
        if self.custom_post_save_path_line_edit.text() != '':
            base = self.custom_post_save_path_line_edit.text()
        else:
            if self.object_type == 'USER':
                base = self.settings_manager.user_save_directory
            else:
                base = self.settings_manager.subreddit_save_directory
        path = TokenParser.parse_tokens(self.post, self.post_save_path_structure_line_edit.text())
        title = TokenParser.parse_tokens(self.post, self.post_download_naming_line_edit.text())
        self.post_path_example_label.setText(f'{base}/{path}/{title}')

    def sync_comment_path_example(self):
        if self.custom_comment_save_path_line_edit.text() != '':
            base = self.custom_comment_save_path_line_edit.text()
        else:
            if self.object_type == 'USER':
                base = self.settings_manager.user_save_directory
            else:
                base = self.settings_manager.subreddit_save_directory
        path = TokenParser.parse_tokens(self.post, self.comment_save_path_structure_line_edit.text())
        title = TokenParser.parse_tokens(self.post, self.comment_download_naming_line_edit.text())
        self.comment_path_example_label.setText(f'{base}/{path}/{title}')

    def sync_widgets_to_object(self):
        self.sync_optional()
        self.sync_spin_box(self.post_limit_spinbox, 'post_limit')
        self.sync_spin_box(self.score_limit_spinbox, 'post_score_limit')
        self.sync_combo(self.score_limit_operator_combo, 'post_score_limit_operator')
        self.sync_date_limits()
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
        self.sync_line_edit(self.custom_post_save_path_line_edit, 'custom_post_save_path')
        self.sync_post_path_example()
        self.sync_combo(self.comment_extract_combo, 'extract_comments')
        self.sync_combo(self.comment_download_combo, 'download_comments')
        self.sync_combo(self.comment_content_download_combo, 'download_comment_content')
        self.sync_spin_box(self.comment_limit_spinbox, 'comment_limit')
        self.sync_spin_box(self.comment_depth_spinbox, 'comment_depth')
        self.sync_spin_box(self.comment_reply_limit_spinbox, 'comment_reply_limit')
        self.sync_spin_box(self.comment_score_limit_spinbox, 'comment_score_limit')
        self.sync_combo(self.comment_score_operator_combo, 'comment_score_limit_operator')
        self.sync_combo(self.comment_sort_combo, 'comment_sort_method')
        self.sync_combo(self.comment_file_format_combo, 'comment_file_format')
        self.sync_line_edit(self.comment_download_naming_line_edit, 'comment_naming_method')
        self.sync_line_edit(self.comment_save_path_structure_line_edit, 'comment_save_structure')
        self.sync_line_edit(self.custom_comment_save_path_line_edit, 'custom_comment_save_path')
        self.sync_comment_path_example()

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
            if date_limit is not None:
                if date_limit.timestamp() < const.FIRST_POST_EPOCH:
                    self.limit_date_checkbox.setChecked(False)
                else:
                    self.limit_date_checkbox.setChecked(True)
                    self.custom_date_limit_radio.setChecked(True)
                    self.custom_date_limit_edit.setDateTime(date_limit)
            else:
                self.limit_date_checkbox.setChecked(True)
                self.absolute_date_limit_radio.setChecked(True)
                self.custom_date_limit_edit.setDisabled(True)
                self.update_custom_date_limit_radio.setDisabled(True)
                self.do_not_update_custom_date_limit_radio.setDisabled(True)

        abs_date_limit = getattr(self.selected_objects[0], 'absolute_date_limit')
        if all(getattr(x, 'absolute_date_limit') == abs_date_limit for x in self.selected_objects):
            self.absolute_date_limit_label.setText(self.selected_objects[0].absolute_date_limit_display)
        else:
            self.absolute_date_limit_label.setText('---')

        update_limit = getattr(self.selected_objects[0], 'update_date_limit')
        if all(getattr(x, 'update_date_limit') == update_limit for x in self.selected_objects):
            if update_limit:
                self.update_custom_date_limit_radio.setChecked(True)
            else:
                self.do_not_update_custom_date_limit_radio.setChecked(True)
        else:
            self.update_custom_date_limit_radio.setChecked(False)
            self.do_not_update_custom_date_limit_radio.setChecked(False)

    def choose_file_path(self):
        default = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder = str(QFileDialog.getExistingDirectory(self, 'Select Custom Save Directory', default))
        if os.path.isdir(folder):
            return folder
        return None
