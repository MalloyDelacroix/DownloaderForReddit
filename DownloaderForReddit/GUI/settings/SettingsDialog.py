from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from DownloaderForReddit.GUI_Resources.settings.SettingsDialog_auto import Ui_SettingsDialog
from . import CoreSettingsWidget, DownloadSettingsWidget, DisplaySettingsWidget
from DownloaderForReddit.Utils import Injector


class SettingsDialog(QDialog, Ui_SettingsDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings_manager = Injector.get_settings_manager()

        geom = self.settings_manager.settings_dialog_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 or geom['y'] != 0:
            self.move(geom['x'], geom['y'])

        self.settings_map = {
            'Core': CoreSettingsWidget(),
            'Download Defaults': DownloadSettingsWidget(),
            'Display': DisplaySettingsWidget(),
        }

        for item in self.settings_map.keys():
            self.settings_list_widget.addItem(item)

        self.current_display = None
        self.settings_list_widget.currentItemChanged.connect(lambda x: self.set_current_display(x.text()))
        self.settings_list_widget.setCurrentRow(0)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.close)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    def set_current_display(self, view_name):
        widget = self.settings_map[view_name]
        if not widget.loaded:
            widget.load_settings()
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
            view.apply_settings()
        self.settings_manager.save_all()

    def closeEvent(self, event):
        self.settings_manager.settings_dialog_geom = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y()
        }
        super().closeEvent(event)
