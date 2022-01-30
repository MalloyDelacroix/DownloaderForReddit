from datetime import date, datetime
from PyQt5.QtWidgets import QCheckBox, QColorDialog, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor

from DownloaderForReddit.guiresources.settings.display_settings_widget_auto import Ui_DispalySettingsWidget
from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.core import const
from DownloaderForReddit.utils import general_utils


class DisplaySettingsWidget(AbstractSettingsWidget, Ui_DispalySettingsWidget):

    def __init__(self, **kwargs):
        super().__init__()
        self.main_window = kwargs.get('main_window', None)
        self.grid = self.tooltip_groupbox.layout()
        self.colors = {}
        self.tooltips = {}
        self.date_tokens = [
            ('%a', 'Weekday as locale’s abbreviated name.', 'Mon'),
            ('%A', 'Weekday as locale’s full name.', 'Monday'),
            ('%w', 'Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.', '1'),
            ('%d', 'Day of the month as a zero-padded decimal number.', '30'),
            ('%-d', 'Day of the month as a decimal number. (Platform specific)', '30'),
            ('%b', 'Month as locale’s abbreviated name.', 'Sep'),
            ('%B', 'Month as locale’s full name.', 'September'),
            ('%m', 'Month as a zero-padded decimal number.', '09'),
            ('%-m', 'Month as a decimal number. (Platform specific)', '9'),
            ('%y', 'Year without century as a zero-padded decimal number.', '13'),
            ('%Y', 'Year with century as a decimal number.', '2013'),
            ('%j', 'Day of the year as a zero-padded decimal number.', '273'),
            ('%-j', 'Day of the year as a decimal number. (Platform specific)', '273'),
            ('%U',
             'Week number of the year (Sunday as the first day of the week) as a zero padded decimal number. All days '
             'in a new year preceding the first Sunday are considered to be in week 0.', '39'),
            ('%W',
             'Week number of the year (Monday as the first day of the week) as a decimal number. All days in a new '
             'year preceding the first Monday are considered to be in week 0.', '39'),
            ('%c', 'Locale’s appropriate date and time representation.', 'Mon Sep 30 07:06:05 2013'),
            ('%x', 'Locale’s appropriate date representation.', '09/30/13'),
            ('%X', 'Locale’s appropriate time representation.', '07:06:05'),
        ]
        self.time_tokens = [
            ('%H', 'Hour (24-hour clock) as a zero-padded decimal number.', '07'),
            ('%-H', 'Hour (24-hour clock) as a decimal number. (Platform specific)', '7'),
            ('%I', 'Hour (12-hour clock) as a zero-padded decimal number.', '07'),
            ('%-I', 'Hour (12-hour clock) as a decimal number. (Platform specific)', '7'),
            ('%p', 'Locale’s equivalent of either AM or PM.', 'AM'),
            ('%M', 'Minute as a zero-padded decimal number.', '06'),
            ('%-M', 'Minute as a decimal number. (Platform specific)', '6'),
            ('%S', 'Second as a zero-padded decimal number.', '05'),
            ('%-S', 'Second as a decimal number. (Platform specific)', '5'),
            ('%f', 'Microsecond as a decimal number, zero-padded on the left.', '000000'),
            ('%Z', 'Time zone name (empty string if the object is naive).'),
        ]

        self.datetime_token_button.clicked.connect(self.datetime_token_context_menu)
        self.date_token_button.clicked.connect(self.date_token_context_menu)

        self.datetime_format_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.datetime_format_line_edit.customContextMenuRequested.connect(self.datetime_token_context_menu)
        self.datetime_format_line_edit.textChanged.connect(
            lambda: self.set_date_example(self.datetime_format_line_edit, self.date_time_format_example_label)
        )

        self.date_format_line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.date_format_line_edit.customContextMenuRequested.connect(self.date_token_context_menu)
        self.date_format_line_edit.textChanged.connect(
            lambda: self.set_date_example(self.date_format_line_edit, self.date_format_example_label)
        )

        for value in self.settings.countdown_view_choices:
            self.schedule_countdown_combo.addItem(value.replace('_', ' ').title(), value)

        self.choose_new_color_button.clicked.connect(self.choose_new_color)
        self.choose_disabled_color_button.clicked.connect(self.choose_disabled_color)
        self.choose_inactive_color_button.clicked.connect(self.choose_inactive_color)
        self.tooltip_checkbox_count = 0

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
        self.datetime_format_line_edit.setText(self.settings.datetime_display_format)
        self.date_format_line_edit.setText(self.settings.date_display_format)
        for key, value in self.settings.main_window_tooltip_display_dict.items():
            self.add_tooltip_setting_checkbox(key, value)

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

    def add_tooltip_setting_checkbox(self, attr, checked):
        checkbox = QCheckBox(attr.replace('_', ' ').title())
        checkbox.setChecked(checked)
        self.grid.addWidget(checkbox, self.tooltip_checkbox_count // 2, self.tooltip_checkbox_count % 2)
        self.tooltips[attr] = checkbox
        self.tooltip_checkbox_count += 1

    def datetime_token_context_menu(self):
        menu = QMenu()
        for tup in self.date_tokens + self.time_tokens:
            menu.addAction(': '.join(tup),
                           lambda token=tup[0]: self.insert_token(self.datetime_format_line_edit, token))
        menu.exec_(QCursor.pos())

    def date_token_context_menu(self):
        menu = QMenu()
        for tup in self.date_tokens:
            menu.addAction(': '.join(tup),
                           lambda token=tup[0]: self.insert_token(self.date_format_line_edit, token))
        menu.exec_(QCursor.pos())

    def insert_token(self, line_edit, token):
        if line_edit.hasSelectedText():
            line_edit.del_()
        line_edit.insert(token)

    def set_date_example(self, line_edit, example_label):
        d = date.fromtimestamp(const.FIRST_POST_EPOCH)
        date_format = line_edit.text()
        try:
            example_label.setText(general_utils.format_raw_datetime(d, date_format))
            example_label.setStyleSheet('color: black;')
        except ValueError:
            example_label.setText('Invalid format string')
            example_label.setStyleSheet('color: red;')

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
        if self.test_date_format(self.datetime_format_line_edit.text()):
            self.settings.datetime_display_format = self.datetime_format_line_edit.text()
        if self.test_date_format(self.date_format_line_edit.text()):
            self.settings.date_display_format = self.date_format_line_edit.text()
        for attr, checkbox in self.tooltips.items():
            self.settings.main_window_tooltip_display_dict[attr] = checkbox.isChecked()

    def test_date_format(self, date_format):
        d = datetime.fromtimestamp(const.FIRST_POST_EPOCH)
        try:
            general_utils.format_raw_datetime(d, date_format)
            return True
        except ValueError:
            return False
