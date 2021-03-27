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

        self.show_system_tray_icon_checkbox.toggled.connect(self.set_checkboxes_enabled)
        self.show_system_tray_notifications_checkbox.toggled.connect(self.set_checkboxes_enabled)

    def set_checkboxes_enabled(self):
        self.show_system_tray_notifications_checkbox.setEnabled(self.show_system_tray_icon_checkbox.isChecked())
        self.status_tray_message_display_length_spinbox.setEnabled(
            self.show_system_tray_icon_checkbox.isChecked() and self.show_system_tray_notifications_checkbox.isChecked()
        )

    def load_settings(self):
        self.update_level_combo.setCurrentIndex(self.settings.update_notification_level)
        self.auto_display_failed_downloads_checkbox.setChecked(self.settings.auto_display_failed_downloads)
        self.remove_reddit_object_warning_checkbox.setChecked(self.settings.remove_reddit_object_warning)
        self.remove_reddit_object_list_warning_checkbox.setChecked(self.settings.remove_reddit_object_list_warning)
        self.ask_to_sync_on_move_checkbox.setChecked(self.settings.ask_to_sync_moved_ro_settings)
        self.large_post_update_warning_checkbox.setChecked(self.settings.large_post_update_warning)
        self.existing_reddit_object_dialog_checkbox.setChecked(self.settings.check_existing_reddit_objects)
        self.show_system_tray_icon_checkbox.setChecked(self.settings.show_system_tray_icon)
        self.show_system_tray_notifications_checkbox.setChecked(self.settings.show_system_tray_notifications)
        self.status_tray_message_display_length_spinbox.setValue(self.settings.tray_icon_message_display_length)

    def apply_settings(self):
        self.settings.update_notification_level = self.update_level_combo.currentData(Qt.UserRole)
        self.settings.auto_display_failed_downloads = self.auto_display_failed_downloads_checkbox.isChecked()
        self.settings.remove_reddit_object_warning = self.remove_reddit_object_warning_checkbox.isChecked()
        self.settings.remove_reddit_object_list_warning = \
            self.remove_reddit_object_list_warning_checkbox.isChecked()
        self.settings.ask_to_sync_moved_ro_settings = self.ask_to_sync_on_move_checkbox.isChecked()
        self.settings.large_post_update_warning = self.large_post_update_warning_checkbox.isChecked()
        self.settings.check_existing_reddit_objects = self.existing_reddit_object_dialog_checkbox.isChecked()
        self.settings.show_system_tray_icon = self.show_system_tray_icon_checkbox.isChecked()
        self.settings.show_system_tray_notifications = self.show_system_tray_notifications_checkbox.isChecked()
        self.settings.tray_icon_message_display_length = self.status_tray_message_display_length_spinbox.value()
