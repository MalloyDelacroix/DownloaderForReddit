from PyQt5.QtWidgets import QCheckBox, QColorDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from DownloaderForReddit.guiresources.settings.display_settings_widget_auto import Ui_DispalySettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget


class DisplaySettingsWidget(AbstractSettingsWidget, Ui_DispalySettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()
        self.main_window = kwargs.get('main_window', None)
        self.grid = self.tooltip_groupbox.layout()
        self.colors = {}
        self.tooltips = {}

        for value in self.settings.countdown_view_choices:
            self.schedule_countdown_combo.addItem(value.replace('_', ' ').title(), value)

        self.choose_new_color_button.clicked.connect(self.choose_new_color)
        self.choose_disabled_color_button.clicked.connect(self.choose_disabled_color)
        self.choose_inactive_color_button.clicked.connect(self.choose_inactive_color)

    def load_settings(self):
        self.short_title_length_spin_box.setValue(self.settings.short_title_char_length)
        self.schedule_countdown_combo.setCurrentIndex(
            self.settings.countdown_view_choices.index(self.settings.show_schedule_countdown))
        self.scroll_to_last_added_checkbox.setChecked(self.settings.scroll_to_last_added)
        self.colors['new'] = self.settings.new_reddit_object_display_color
        self.colors['disabled'] = self.settings.disabled_reddit_object_display_color
        self.colors['inactive'] = self.settings.inactive_reddit_object_display_color
        self.colorize_new_checkbox.setChecked(self.settings.colorize_new_reddit_objects)
        self.colorize_disabled_checkbox.setChecked(self.settings.colorize_disabled_reddit_objects)
        self.colorize_inactive_checkbox.setChecked(self.settings.colorize_inactive_reddit_objects)
        self.set_new_color_label()
        self.set_disabled_color_label()
        self.set_inactive_color_label()

        for key, value in self.settings.main_window_tooltip_display_dict.items():
            self.add_checkbox(key, value)

    def set_new_color_label(self):
        r, g, b = self.colors['new']
        self.new_ro_color_label.setStyleSheet(
            f'background-color: white;'
            f'color: rgb({r}, {g}, {b});'
        )

    def set_disabled_color_label(self):
        r, g, b = self.colors['disabled']
        self.disabled_ro_color_label.setStyleSheet(
            f'background-color: white;'
            f'color: rgb({r}, {g}, {b});'
        )

    def set_inactive_color_label(self):
        r, g, b = self.colors['inactive']
        self.inactive_ro_color_label.setStyleSheet(
            f'background-color: white;'
            f'color: rgb({r}, {g}, {b});'
        )

    def choose_new_color(self):
        color = self.choose_color('new')
        if color is not None:
            self.colors['new'] = [color.red(), color.green(), color.blue()]
            self.set_new_color_label()

    def choose_disabled_color(self):
        color = self.choose_color('disabled')
        if color is not None:
            self.colors['disabled'] = [color.red(), color.green(), color.blue()]
            self.set_disabled_color_label()

    def choose_inactive_color(self):
        color = self.choose_color('inactive')
        if color is not None:
            self.colors['inactive'] = [color.red(), color.green(), color.blue()]
            self.set_inactive_color_label()

    def choose_color(self, key):
        init_color = QColor(*self.colors[key])
        color = QColorDialog.getColor(initial=init_color, title=f'Choose {key.title()} Color')
        if color.isValid():
            return color
        return None

    def add_checkbox(self, attr, checked):
        checkbox = QCheckBox(attr.replace('_', ' ').title())
        checkbox.setChecked(checked)
        self.grid.addWidget(checkbox)
        self.tooltips[attr] = checkbox

    def apply_settings(self):
        self.settings.short_title_char_length = self.short_title_length_spin_box.value()
        show_countdown = self.schedule_countdown_combo.currentData(Qt.UserRole)
        self.settings.show_schedule_countdown = show_countdown
        self.main_window.schedule_widget.setVisible(show_countdown == 'SHOW')
        self.settings.scroll_to_last_added = self.scroll_to_last_added_checkbox.isChecked()
        self.settings.colorize_new_reddit_objects = self.colorize_new_checkbox.isChecked()
        self.settings.colorize_disabled_reddit_objects = self.colorize_disabled_checkbox.isChecked()
        self.settings.colorize_inactive_reddit_objects = self.colorize_inactive_checkbox.isChecked()
        self.settings.new_reddit_object_display_color = self.colors['new']
        self.settings.disabled_reddit_object_display_color = self.colors['disabled']
        self.settings.inactive_reddit_object_display_color = self.colors['inactive']
        for attr, checkbox in self.tooltips.items():
            self.settings.main_window_tooltip_display_dict[attr] = checkbox.isChecked()
