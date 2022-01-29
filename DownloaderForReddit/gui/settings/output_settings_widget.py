from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtCore import Qt

from DownloaderForReddit.guiresources.settings.output_settings_widget_auto import Ui_OutputSettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget
from ...messaging.message import MessagePriority


class OutputSettingsWidget(AbstractSettingsWidget, Ui_OutputSettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()
        self.main_window = kwargs.get('main_window', None)
        self.colors = {}
        for x in MessagePriority:
            self.priority_level_combo.addItem(x.name, x)
            self.connect_color_picker_buttons(x.name.lower())
        self.debug_color_label.setStyleSheet('background-color: white;')

    def connect_color_picker_buttons(self, priority):
        button = getattr(self, f'change_{priority.lower()}_color_button')
        button.clicked.connect(lambda: self.pick_color(priority))

    def load_settings(self):
        self.priority_level_combo.setCurrentText(self.settings.output_priority_level.name)
        self.show_priority_level_checkbox.setChecked(self.settings.show_priority_level)
        self.clear_on_run_checkbox.setChecked(self.settings.clear_messages_on_run)
        self.output_saved_content_full_path_checkbox.setChecked(self.settings.output_saved_content_full_path)
        self.color_groupbox.setChecked(self.settings.use_color_output)

        for x in MessagePriority:
            self.colors[x.name.lower()] = getattr(self.settings, f'{x.name.lower()}_color')

        self.set_label_stylesheet('debug')
        self.set_label_stylesheet('info')
        self.set_label_stylesheet('warning')
        self.set_label_stylesheet('error')
        self.set_label_stylesheet('critical')
        self.set_label_stylesheet('requested')

    def set_label_stylesheet(self, priority):
        r, g, b = self.colors[priority]
        label = getattr(self, f'{priority}_color_label')
        label.setStyleSheet(
            f'background-color: white;'
            f'color: rgb({r}, {g}, {b});'
        )

    def parse_color(self, priority):
        r, g, b = getattr(self.settings, f'{priority}_color')
        return f'{r}, {g}, {b}'

    def pick_color(self, priority):
        color = QColorDialog.getColor()
        self.colors[priority] = [color.red(), color.green(), color.blue()]
        self.set_label_stylesheet(priority)

    def apply_settings(self):
        priority = self.priority_level_combo.currentData(Qt.UserRole)
        if priority != self.settings.output_priority_level:
            self.settings.output_priority_level = self.priority_level_combo.currentData(Qt.UserRole)
            self.main_window.update_output()
        self.settings.show_priority_level = self.show_priority_level_checkbox.isChecked()
        self.settings.clear_messages_on_run = self.clear_on_run_checkbox.isChecked()
        self.settings.output_saved_content_full_path = self.output_saved_content_full_path_checkbox.isChecked()
        self.settings.use_color_output = self.color_groupbox.isChecked()
        for key, value in self.colors.items():
            setattr(self.settings, f'{key}_color', value)
