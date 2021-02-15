from PyQt5.QtCore import Qt

from DownloaderForReddit.guiresources.settings.notification_settings_widget_auto import Ui_NotificationSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class NotificationSettingsWidget(AbstractSettingsWidget, Ui_NotificationSettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()
        level_map = {
            0: 'All Releases',
            1: 'Minor Release',
            2: 'Major Release',
            3: 'Do Not Notify'
        }
        for key, value in level_map.items():
            self.update_level_combo.addItem(value, key)

    def load_settings(self):
        self.update_level_combo.setCurrentIndex(self.settings.update_notification_level)
        self.auto_display_failed_downloads_checkbox.setChecked(self.settings.auto_display_failed_downloads)
        self.remove_reddit_object_warning_checkbox.setChecked(self.settings.remove_reddit_object_warning)
        self.remove_reddit_object_list_warning_checkbox.setChecked(self.settings.remove_reddit_object_list_warning)
        self.large_post_update_warning_checkbox.setChecked(self.settings.large_post_update_warning)
        self.existing_reddit_object_dialog_checkbox.setChecked(self.settings.check_existing_reddit_objects)

    def apply_settings(self):
        self.settings.update_notification_level = self.update_level_combo.currentData(Qt.UserRole)
        self.settings.auto_display_failed_downloads = self.auto_display_failed_downloads_checkbox.isChecked()
        self.settings.remove_reddit_object_warning = self.remove_reddit_object_warning_checkbox.isChecked()
        self.settings.remove_reddit_object_list_warning = \
            self.remove_reddit_object_list_warning_checkbox.isChecked()
        self.settings.large_post_update_warning = self.large_post_update_warning_checkbox.isChecked()
        self.settings.check_existing_reddit_objects = self.existing_reddit_object_dialog_checkbox.isChecked()
