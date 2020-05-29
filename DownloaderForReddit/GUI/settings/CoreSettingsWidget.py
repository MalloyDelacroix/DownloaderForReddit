from PyQt5.QtWidgets import QWidget

from DownloaderForReddit.GUI_Resources.settings.CoreSettingsWidget_auto import Ui_CoreSettingsWidget
from .AbstractSettingsWidget import AbstractSettingsWidget


class CoreSettingsWidget(AbstractSettingsWidget, Ui_CoreSettingsWidget):

    def __init__(self):
        super().__init__()

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
