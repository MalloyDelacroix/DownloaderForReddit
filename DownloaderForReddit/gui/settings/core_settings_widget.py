from PyQt5.QtGui import QValidator

from DownloaderForReddit.guiresources.settings.core_settings_widget_auto import Ui_CoreSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.utils import general_utils, system_util


class CoreSettingsWidget(AbstractSettingsWidget, Ui_CoreSettingsWidget):

    def __init__(self):
        super().__init__()
        self.rename_invalid_download_folders_checkbox.toggled.connect(self.toggle_invalid_name_options)
        self.invalid_rename_format_line_edit.setValidator(FormatValidator())
        self.invalid_rename_format_line_edit.textChanged.connect(self.set_example)
        self.user_save_dir_line_edit.textChanged.connect(self.set_example)

    def load_settings(self):
        self.user_save_dir_line_edit.setText(self.settings.user_save_directory)
        self.subreddit_save_dir_line_edit.setText(self.settings.subreddit_save_directory)
        self.match_date_modified_checkbox.setChecked(self.settings.match_file_modified_to_post_date)
        self.rename_invalid_download_folders_checkbox.setChecked(
            self.settings.rename_invalidated_download_folders)
        if not self.settings.rename_invalidated_download_folders:
            self.invalid_rename_format_line_edit.setDisabled(True)
        self.invalid_rename_format_line_edit.setText(self.settings.invalid_rename_format)

        self.extraction_thread_count_spinbox.setValue(self.settings.extraction_thread_count)
        self.download_thread_count_spinbox.setValue(self.settings.download_thread_count)
        self.download_on_add_checkbox.setChecked(self.settings.download_on_add)
        self.finish_incomplete_extractions_checkbox.setChecked(
            self.settings.finish_incomplete_extractions_at_session_start)
        self.finish_incomplete_downloads_checkbox.setChecked(
            self.settings.finish_incomplete_downloads_at_session_start)
        self.download_reddit_hosted_videos_checkbox.setChecked(self.settings.download_reddit_hosted_videos)

    def apply_settings(self):
        self.settings.user_save_directory = self.user_save_dir_line_edit.text()
        self.settings.subreddit_save_directory = self.subreddit_save_dir_line_edit.text()
        self.settings.match_file_modified_to_post_date = self.match_date_modified_checkbox.isChecked()
        self.settings.rename_invalidated_download_folders = self.rename_invalid_download_folders_checkbox.isChecked()
        self.settings.invalid_rename_format = self.invalid_rename_format_line_edit.text()

        self.settings.extraction_thread_count = self.extraction_thread_count_spinbox.value()
        self.settings.download_thread_count = self.download_thread_count_spinbox.value()
        self.settings.finish_incomplete_extractions_at_session_start = \
            self.finish_incomplete_extractions_checkbox.isChecked()
        self.settings.finish_incomplete_downloads_at_session_start = \
            self.finish_incomplete_downloads_checkbox.isChecked()
        self.settings.download_reddit_hosted_videos = self.download_reddit_hosted_videos_checkbox.isChecked()

    def toggle_invalid_name_options(self):
        enabled = not self.rename_invalid_download_folders_checkbox.isChecked()
        self.invalid_rename_format_line_edit.setDisabled(enabled)
        self.invalid_format_example_label.setDisabled(enabled)
        self.invalid_rename_label.setDisabled(enabled)
        self.example_label.setDisabled(enabled)

    def set_example(self):
        example_path = system_util.join_path(self.user_save_dir_line_edit.text(), 'example_directory')
        renamed_example = general_utils.reformat_invalid_name(example_path, self.invalid_rename_format_line_edit.text())
        self.invalid_format_example_label.setText(renamed_example)


class FormatValidator(QValidator):

    def __init__(self):
        super().__init__()

    def validate(self, text, pos):
        if '%[dir_name]' in text:
            return QValidator.Acceptable, text, pos
        else:
            return QValidator.Invalid, text, pos
