import os
from time import time
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QSizePolicy,
                             QCheckBox, QLineEdit, QPushButton)
from PyQt5.QtGui import QColor

from .abstract_settings_widget import AbstractSettingsWidget
from DownloaderForReddit.core import const
from DownloaderForReddit.gui import message_dialogs


class SupportedVideoSettingsWidget(AbstractSettingsWidget):
    background_color = QColor('#ffffff')
    highlight_color = QColor('#ffd480')

    def __init__(self):
        super().__init__(init_ui=False)
        self.setWindowTitle('Supported Video Sites')
        self.supported_sites_path = os.path.join(const.RESOURCES, 'supported_video_sites.txt')
        self.default_sites = []
        self.valid_sites = []
        self.site_map = {}

        layout = QVBoxLayout()
        text = 'This is a list of sites that are supported by the youtube-dl project which this application uses to ' \
               'extend the number of video host sites that it supports.  The list is pulled directly from the list of '\
               'supported sites found on their website.  Uncheck any of these sites to disable download from them.\n\n'\
               'It is recommended that you modify this list of sites to better fit your needs.  Due to the shear ' \
               'number of sites that are supported, matching character keys in some urls may produce false ' \
               'positives.  This should not adversely affect the application except that it may prolong download run ' \
               'time.\n'

        info_label = QLabel(text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search')
        self.search_bar.textChanged.connect(self.search_sites)
        self.found_label = QLabel('0')
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(QLabel('Found: '))
        search_layout.addWidget(self.found_label)
        layout.addLayout(search_layout)

        self.list_widget = QListWidget()
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.list_widget)

        button_box = QHBoxLayout()
        self.select_all_button = QPushButton('Select All')
        self.clear_selection_button = QPushButton('Clear All')
        self.select_all_button.clicked.connect(self.select_all)
        self.clear_selection_button.clicked.connect(self.clear_selection)
        button_box.addWidget(self.select_all_button)
        button_box.addWidget(self.clear_selection_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def load_settings(self):
        with open(self.supported_sites_path, 'r') as file:
            for line in file.readlines():
                site = line.strip()
                checked = False
                if site.endswith('*'):
                    checked = True
                    site = site.strip('*')
                self.add_widget(site, checked)

    def add_widget(self, site, checked):
        checkbox = QCheckBox(site)
        checkbox.setChecked(checked)

        item = QListWidgetItem()
        item.setSizeHint(checkbox.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, checkbox)
        self.site_map[site] = checkbox
        setattr(item, 'site', site)

    def apply_settings(self):
        try:
            with open(self.supported_sites_path, 'w') as file:
                for site, checkbox in self.site_map.items():
                    if checkbox.isChecked():
                        site = site + '*'
                    file.write(site + '\n')
            self.settings.supported_videos_updated = time()
        except PermissionError:
            message_dialogs.error_dialog(
                self,
                'Permission Denied',
                'Unable to save changes to supported video sites file.  Permission denied.\n\n'
                'Please make sure you have write permission to the directory that the application files are located.'
            )

    def search_sites(self, text):
        if text is not None and text != '':
            found = 0
            first_item = None
            for x in range(self.list_widget.count()):
                item = self.list_widget.item(x)
                if text in item.site:
                    found += 1
                    color = self.highlight_color
                    if first_item is None:
                        first_item = item
                else:
                    color = self.background_color
                item.setBackground(color)
            self.found_label.setText(str(found))
            if first_item is not None:
                self.list_widget.scrollToItem(first_item)
        else:
            for x in range(self.list_widget.count()):
                self.list_widget.item(x).setBackground(self.background_color)
            self.found_label.setText('0')

    def select_all(self):
        for checkbox in self.site_map.values():
            checkbox.setChecked(True)

    def clear_selection(self):
        for checkbox in self.site_map.values():
            checkbox.setChecked(False)
