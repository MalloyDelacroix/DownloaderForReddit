import logging
from datetime import datetime
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor

from ..GUI_Resources.RedditObjectSettingsDialog_auto import Ui_RedditObjectSettingsDialog
from ..ViewModels.RedditObjectListModel import RedditObjectListModel
from ..Database.Models import Post, Content, Comment
from ..Database.ModelEnums import *
from ..Utils import Injector
from ..Utils.TokenParser import TokenParser


class RedditObjectSettingsDialog(QtWidgets.QDialog, Ui_RedditObjectSettingsDialog):
    download_signal = pyqtSignal(int)

    def __init__(self, list_type, list_name, selected_object_id: int):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = Injector.get_database_handler()
        self.list_type = list_type
        self.list_name = list_name
        self.selected_object = None

        self.dialog_button_box.accepted.connect(self.save_and_close)
        self.dialog_button_box.rejected.connect(self.close)
        self.reset_button.clicked.connect(self.reset)

        self.reddit_objects_list_view.clicked.connect(
            lambda x: self.change_objects(self.list_model.data(x, 'RAW_DATA'))
        )
        self.list_model = RedditObjectListModel(self.list_type)
        self.list_model.set_list(self.list_name)
        self.reddit_objects_list_view.setModel(self.list_model)
        index = self.list_model.index(self.list_model.get_id_list().index(selected_object_id), 0)
        self.selected_object = self.list_model.data(index, 'RAW_DATA')
        self.reddit_objects_list_view.setCurrentIndex(index)

        self.setup_widgets()
        self.sync_all()
        self.connect_edit_widgets()

    def change_objects(self, new_object):
        self.selected_object = new_object
        self.sync_all()

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
            self.comment_download_combo.addItem(value.display_name, value)
            self.comment_content_download_combo.addItem(value.display_name, value)
        for value in CommentSortMethod:
            self.comment_sort_combo.addItem(value.display_name, value)

        self.download_naming_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.download_naming_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.download_naming_line_edit))
        self.download_naming_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.download_naming_line_edit))
        self.save_path_structure_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.save_path_structure_line_edit.customContextMenuRequested.connect(
            lambda: self.path_token_context_menu(self.save_path_structure_line_edit))
        self.save_structure_available_tokens_button.clicked.connect(
            lambda: self.path_token_context_menu(self.save_path_structure_line_edit))

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
        self.download_naming_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'download_naming_method', self.download_naming_line_edit.text()))
        self.save_path_structure_line_edit.editingFinished.connect(
            lambda: setattr(self.selected_object, 'save_structure', self.save_path_structure_line_edit.text()))
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
        menu = QtWidgets.QMenu()
        for key in TokenParser.token_dict.keys():
            menu.addAction(key.replace('_', ' ').title(), lambda token=key: line_edit.insert(f'%[{token}]'))
        menu.exec_(QCursor.pos())

    def sync_all(self):
        self.set_basic_info()
        self.set_download_info()
        self.sync_widgets_to_reddit_object()

    def set_basic_info(self):
        self.name_label.setText(self.selected_object.name)
        self.id_label.setText(str(self.selected_object.id))
        self.date_created_label.setText(self.selected_object.date_created_display)
        self.date_added_label.setText(self.selected_object.date_added_display)
        self.last_download_label.setText(self.selected_object.last_download_display)

    def set_download_info(self):
        self.download_info_thread = Thread(target=self.set_download_info_labels)
        self.download_info_thread.start()

    def set_download_info_labels(self):
        with self.db.get_scoped_session() as session:
            post_count = session.query(Post.id) \
                .filter(Post.significant_reddit_object_id == self.selected_object.id).count()
            comment_count = session.query(Comment.id).join(Post) \
                .filter(Post.significant_reddit_object_id == self.selected_object.id).count()
            content_count = session.query(Content.id) \
                .filter(Content.post_id.in_(session.query(Post.id).filter(
                Post.significant_reddit_object_id == self.selected_object.id))).count()
            self.post_count_label.setText(str(post_count))
            self.comment_count_label.setText(str(comment_count))
            self.content_count_label.setText(str(content_count))

    def sync_widgets_to_reddit_object(self):
        self.download_button.setText(f'Download {self.selected_object.name}')
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
        self.download_naming_line_edit.setText(self.selected_object.download_naming_method)
        self.save_path_structure_line_edit.setText(self.selected_object.save_structure)
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

    def save_and_close(self):
        self.list_model.session.commit()
        self.close()

    def reset(self):
        self.list_model.session.rollback()
        self.sync_all()

    def download(self):
        self.download_signal.emit(self.selected_object.id)
