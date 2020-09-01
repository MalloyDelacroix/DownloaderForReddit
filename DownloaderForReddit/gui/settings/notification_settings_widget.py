from DownloaderForReddit.guiresources.settings.notification_settings_widget_auto import Ui_NotificationSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class NotificationSettingsWidget(AbstractSettingsWidget, Ui_NotificationSettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()

    def load_settings(self):
        self.auto_display_failed_downloads_checkbox.setChecked(self.settings.auto_display_failed_downloads)
        self.remove_reddit_object_warning_checkbox.setChecked(self.settings.remove_reddit_object_warning)
        self.remove_reddit_object_list_warning_checkbox.setChecked(self.settings.remove_reddit_object_list_warning)
        self.large_post_update_warning_checkbox.setChecked(self.settings.large_post_update_warning)
        self.notify_available_updates_checkbox.setChecked(self.settings.notify_update)

    def apply_settings(self):
        self.settings.auto_display_failed_downloads = self.auto_display_failed_downloads_checkbox.isChecked()
        self.settings.remove_reddit_object_warning = self.remove_reddit_object_warning_checkbox.isChecked()
        self.settings.remove_reddit_object_list_warning = \
            self.remove_reddit_object_list_warning_checkbox.isChecked()
        self.settings.large_post_update_warning = self.large_post_update_warning_checkbox.isChecked()
        self.settings.notify_update = self.notify_available_updates_checkbox.isChecked()
