from PyQt5.QtWidgets import QCheckBox

from DownloaderForReddit.guiresources.settings.display_settings_widget_autp import Ui_DispalySettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class DisplaySettingsWidget(AbstractSettingsWidget, Ui_DispalySettingsWidget):

    def __init__(self):
        super().__init__()
        self.grid = self.tooltip_groupbox.layout()
        self.tooltips = {}

    def load_settings(self):
        self.short_title_length_spin_box.setValue(self.settings.short_title_char_length)
        for key, value in self.settings.main_window_tooltip_display_dict.items():
            self.add_checkbox(key, value)

    def add_checkbox(self, attr, checked):
        checkbox = QCheckBox(attr.replace('_', ' ').title())
        checkbox.setChecked(checked)
        self.grid.addWidget(checkbox)
        self.tooltips[attr] = checkbox

    def apply_settings(self):
        self.settings.short_title_char_length = self.short_title_length_spin_box.value()
        for attr, checkbox in self.tooltips.items():
            self.settings.main_window_tooltip_display_dict[attr] = checkbox.isChecked()
