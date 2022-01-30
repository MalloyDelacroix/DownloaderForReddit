from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from DownloaderForReddit.guiresources.settings.settings_dialog_auto import Ui_SettingsDialog
from .core_settings_widget import CoreSettingsWidget
from .download_settings_widget import DownloadSettingsWidget
from .display_settings_widget import DisplaySettingsWidget
from .output_settings_widget import OutputSettingsWidget
from .imgur_settings_widget import ImgurSettingsWidget
from .database_settings_widget import DatabaseSettingsWidget
from .schedule_settings_widget import ScheduleSettingsWidget
from .supported_video_settings_widget import SupportedVideoSettingsWidget
from .quick_filter_settings_widget import QuickFilterSettingsWidget
from .default_filter_settings_widget import DefaultFilterSettingsWidget
from .notification_settings_widget import NotificationSettingsWidget
from DownloaderForReddit.utils import injector


class SettingsDialog(QDialog, Ui_SettingsDialog):

    def __init__(self, parent=None, **kwargs):
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.parent = parent
        self.settings_manager = injector.get_settings_manager()

        geom = self.settings_manager.settings_dialog_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 or geom['y'] != 0:
            self.move(geom['x'], geom['y'])

        self.settings_map = {
            'Core': CoreSettingsWidget(),
            'Download Defaults': DownloadSettingsWidget(main_window=self.parent, **kwargs),
            'Display': DisplaySettingsWidget(main_window=self.parent),
            'Output': OutputSettingsWidget(main_window=self.parent),
            'Imgur': ImgurSettingsWidget(),
            'Scheduled Downloads': ScheduleSettingsWidget(),
            'Video Sites': SupportedVideoSettingsWidget(),
            'Database View': DatabaseSettingsWidget(),
            'Quick Filters': QuickFilterSettingsWidget(),
            'Default Filters': DefaultFilterSettingsWidget(),
            'Notifications': NotificationSettingsWidget(),
        }

        for item in self.settings_map.keys():
            self.settings_list_widget.addItem(item)

        self.current_display = None
        self.settings_list_widget.currentItemChanged.connect(lambda x: self.set_current_display(x.text()))
        open_display = kwargs.pop('open_display', None)
        if open_display is None:
            self.settings_list_widget.setCurrentRow(0)
        else:
            self.settings_list_widget.setCurrentRow(list(self.settings_map.keys()).index(open_display))

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.close)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    def set_current_display(self, view_name):
        widget = self.settings_map[view_name]
        if not widget.loaded:
            widget.load()
        if self.current_display is not None:
            self.container_layout.removeWidget(self.current_display)
            self.current_display.setVisible(False)
        self.current_display = widget
        self.container_layout.addWidget(widget)
        widget.setVisible(True)
        self.set_labels()

    def set_labels(self):
        """
        Sets the title and description label based on the new current display.
        """
        self.title_label.setText(self.current_display.windowTitle())
        description = self.current_display.description
        self.description_label.setVisible(description is not None)
        self.description_label.setText(description)

    def accept(self):
        self.apply()
        super().accept()

    def apply(self):
        for view in self.settings_map.values():
            view.apply()
        self.settings_manager.save_all()

    def closeEvent(self, event):
        self.settings_manager.settings_dialog_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
        super().closeEvent(event)
