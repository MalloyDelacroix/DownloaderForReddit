from datetime import datetime
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ...GUI_Resources.widgets.ObjectSettingsWidget_auto import Ui_ObjectSettingsWidget
from ...Database.ModelEnums import *
from ...Utils.TokenParser import TokenParser


class ObjectSettingsWidget(QWidget, Ui_ObjectSettingsWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.setup_widgets()
        self.connect_edit_widgets()

    def set_object(self, obj):
        if obj:
            self.selected_object = obj
            self.sync_widgets_to_object()

    def setup_widgets(self):
        for value in LimitOperator:
            self.score_limit_operator_combo.addItem(value.display_name, value)
            self.comment_score_operator_combo.addItem(value.display_name, value)
        self.self_post_file_format_combo.addItems(['.txt', '.html'])
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
        self.post_limit_spinbox.valueChanged.connect(lambda x: setattr(self.selected_object, 'post_limit', x))
        self.score_limit_spinbox.valueChanged.connect(lambda x: setattr(self.selected_object, 'post_score_limit', x))
        self.score_limit_operator_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'post_score_limit_operator',
                              self.score_limit_operator_combo.itemData(x))
        )
        self.date_limit_checkbox.stateChanged.connect(self.date_limit_checkbox_toggled)
        self.date_limit_edit.dateTimeChanged.connect(self.set_date_limit_from_edit)
        self.setup_checkbox(self.avoid_duplicates_checkbox, 'avoid_duplicates')
        self.setup_checkbox(self.extract_self_post_content_checkbox, 'extract_self_post_links')
        self.setup_checkbox(self.download_self_post_text_checkbox, 'download_self_post_text')
        self.self_post_file_format_combo.currentIndexChanged.connect(
            lambda: setattr(self.selected_object, 'self_post_file_format',
                            self.self_post_file_format_combo.currentText().strip('.')))
        self.setup_checkbox(self.download_videos_checkbox, 'download_videos')
        self.setup_checkbox(self.download_images_checkbox, 'download_images')
        self.nsfw_filter_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'download_nsfw', self.nsfw_filter_combo.itemData(x))
        )
        self.post_sort_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'post_sort_method', self.post_sort_combo.itemData(x))
        )
        self.post_download_naming_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'post_download_naming_method', self.post_download_naming_line_edit.text()))
        self.post_save_path_structure_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'post_save_structure',
                            self.post_save_path_structure_line_edit.text()))
        self.comment_extract_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'extract_comments', self.comment_extract_combo.itemData(x))
        )
        self.comment_download_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'download_comments', self.comment_download_combo.itemData(x))
        )
        self.comment_content_download_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'download_comment_content',
                              self.comment_content_download_combo.itemData(x))
        )
        self.comment_limit_spinbox.valueChanged.connect(lambda x: setattr(self.selected_object, 'comment_limit', x))
        self.comment_score_limit_spinbox.valueChanged.connect(lambda x: setattr(self.selected_object,
                                                                                'comment_score_limit', x))
        self.comment_score_operator_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'comment_score_limit_operator',
                              self.comment_score_operator_combo.itemData(x))
        )
        self.comment_sort_combo.currentIndexChanged.connect(
            lambda x: setattr(self.selected_object, 'comment_sort_method', self.comment_sort_combo.itemData(x))
        )
        self.comment_download_naming_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'comment_naming_method',
                            self.comment_download_naming_line_edit.text())
        )
        self.comment_save_path_structure_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'comment_save_structure',
                            self.comment_save_path_structure_line_edit.text())
        )

    def setup_checkbox(self, checkbox, attribute):
        checkbox.stateChanged.connect(lambda: setattr(self.selected_object, attribute, checkbox.isChecked()))

    def date_limit_checkbox_toggled(self):
        checked = self.date_limit_checkbox.isChecked()
        self.date_limit_edit.setDisabled(not checked)
        if checked:
            self.set_date_limit_from_edit()
        else:
            self.selected_object.date_limit = None

    def set_date_limit_from_edit(self):
        epoch = self.date_limit_edit.dateTime().toSecsSinceEpoch()
        self.selected_object.date_limit = datetime.fromtimestamp(epoch)

    def path_token_context_menu(self, line_edit):
        menu = QMenu()
        for key in TokenParser.token_dict.keys():
            menu.addAction(key.replace('_', ' ').title(), lambda token=key: line_edit.insert(f'%[{token}]'))
        menu.exec_(QCursor.pos())

    def sync_widgets_to_object(self):
        self.lock_settings_checkbox.setChecked(self.selected_object.lock_settings)
        self.enable_download_checkbox.setChecked(self.selected_object.download_enabled)
        self.post_limit_spinbox.setValue(self.selected_object.post_limit)
        self.score_limit_spinbox.setValue(self.selected_object.post_score_limit)
        self.score_limit_operator_combo.setCurrentIndex(
            self.score_limit_operator_combo.findData(self.selected_object.post_score_limit_operator))
        self.date_limit_checkbox.setChecked(self.selected_object.date_limit is not None)
        self.date_limit_edit.setDisabled(self.selected_object.date_limit is None)
        if self.selected_object.date_limit is not None:
            self.date_limit_edit.setDateTime(self.selected_object.date_limit)
        self.avoid_duplicates_checkbox.setChecked(self.selected_object.avoid_duplicates)
        self.extract_self_post_content_checkbox.setChecked(self.selected_object.extract_self_post_links)
        self.download_self_post_text_checkbox.setChecked(self.selected_object.download_self_post_text)
        self.self_post_file_format_combo.setCurrentText(self.selected_object.self_post_file_format)
        self.download_videos_checkbox.setChecked(self.selected_object.download_videos)
        self.download_images_checkbox.setChecked(self.selected_object.download_images)
        self.download_gifs_checkbox.setChecked(self.selected_object.download_gifs)
        self.nsfw_filter_combo.setCurrentIndex(self.nsfw_filter_combo.findData(self.selected_object.download_nsfw))
        self.post_sort_combo.setCurrentIndex(self.post_sort_combo.findData(self.selected_object.post_sort_method))
        self.post_download_naming_line_edit.setText(self.selected_object.post_download_naming_method)
        self.post_save_path_structure_line_edit.setText(self.selected_object.post_save_structure)
        self.comment_extract_combo.setCurrentIndex(
            self.comment_extract_combo.findData(self.selected_object.extract_comments))
        self.comment_download_combo.setCurrentIndex(
            self.comment_download_combo.findData(self.selected_object.download_comments))
        self.comment_content_download_combo.setCurrentIndex(
            self.comment_content_download_combo.findData(self.selected_object.download_comment_content))
        self.comment_limit_spinbox.setValue(self.selected_object.comment_limit)
        self.comment_score_limit_spinbox.setValue(self.selected_object.comment_score_limit)
        self.comment_score_operator_combo.setCurrentIndex(
            self.comment_score_operator_combo.findData(self.selected_object.comment_score_limit_operator))
        self.comment_sort_combo.setCurrentIndex(
            self.comment_sort_combo.findData(self.selected_object.comment_sort_method))
        self.comment_download_naming_line_edit.setText(self.selected_object.comment_naming_method)
        self.comment_save_path_structure_line_edit.setText(self.selected_object.comment_save_structure)
