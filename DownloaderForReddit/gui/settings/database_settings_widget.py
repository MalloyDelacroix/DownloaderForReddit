from PyQt5.QtWidgets import QCheckBox

from DownloaderForReddit.guiresources.settings.database_settings_widget_auto import Ui_DatabaseSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class DatabaseSettingsWidget(AbstractSettingsWidget, Ui_DatabaseSettingsWidget):

    def __init__(self):
        super().__init__()
        self.infinite_scroll_map = {}

    def load_settings(self):
        self.download_session_query_limit_spinbox.setValue(self.settings.download_session_query_limit)
        self.reddit_object_query_limit_spinbox.setValue(self.settings.reddit_object_query_limit)
        self.post_query_limit_spinbox.setValue(self.settings.post_query_limit)
        self.content_query_limit_spinbox.setValue(self.settings.content_query_limit)
        self.comment_query_limit_spinbox.setValue(self.settings.comment_query_limit)

        for model in ['download_session', 'reddit_object', 'post', 'content', 'comment']:
            attr = f'database_view_{model}_infinite_scroll'
            value = getattr(self.settings, attr)
            checkbox = QCheckBox(model.replace('_', ' ').title())
            checkbox.setChecked(value)
            self.infinite_scroll_groupbox.layout().addWidget(checkbox)
            self.infinite_scroll_map[attr] = checkbox

    def apply_settings(self):
        self.settings.download_session_query_limit = self.download_session_query_limit_spinbox.value()
        self.settings.reddit_object_query_limit = self.reddit_object_query_limit_spinbox.value()
        self.settings.post_query_limit = self.post_query_limit_spinbox.value()
        self.settings.content_query_limit = self.content_query_limit_spinbox.value()
        self.settings.comment_query_limit = self.comment_query_limit_spinbox.value()
        for key, value in self.infinite_scroll_map.items():
            setattr(self.settings, key, value.isChecked())
