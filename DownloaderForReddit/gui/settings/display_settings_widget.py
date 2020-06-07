from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt

from DownloaderForReddit.guiresources.settings.display_settings_widget_auto import Ui_DispalySettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class DisplaySettingsWidget(AbstractSettingsWidget, Ui_DispalySettingsWidget):

    def __init__(self):
        super().__init__()
        self.grid = self.tooltip_groupbox.layout()
        self.tooltips = {}

        for value in self.settings.countdown_view_choices:
            self.schedule_countdown_combo.addItem(value.replace('_', ' ').title(), value)

    def load_settings(self):
        self.short_title_length_spin_box.setValue(self.settings.short_title_char_length)
        self.schedule_countdown_combo.setCurrentIndex(
            self.settings.countdown_view_choices.index(self.settings.show_schedule_countdown))
        for key, value in self.settings.main_window_tooltip_display_dict.items():
            self.add_checkbox(key, value)

    def add_checkbox(self, attr, checked):
        checkbox = QCheckBox(attr.replace('_', ' ').title())
        checkbox.setChecked(checked)
        self.grid.addWidget(checkbox)
        self.tooltips[attr] = checkbox

    def apply_settings(self):
        self.settings.short_title_char_length = self.short_title_length_spin_box.value()
        self.settings.show_schedule_countdown = self.schedule_countdown_combo.currentData(Qt.UserRole)
        for attr, checkbox in self.tooltips.items():
            self.settings.main_window_tooltip_display_dict[attr] = checkbox.isChecked()
