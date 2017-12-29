from PyQt5.QtWidgets import QDialog

from GUI_Resources.UserFinderSettingsGUI_auto import Ui_UserFinderSettingsGUI
from Core import Injector


class UserFinderSettingsGUI(QDialog, Ui_UserFinderSettingsGUI):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings_manager = Injector.get_settings_manager()

        self.double_click_operation_dict = {
            'DIALOG': self.open_link_in_dialog_radio,
            'BROWSER': self.open_link_in_browser_radio
        }

        self.content_size_radio_dict = {
            'EXTRA_SMALL': self.content_extra_small_radio,
            'SMALL': self.content_small_radio,
            'MEDIUM': self.content_medium_radio,
            'LARGE': self.content_large_radio,
            'EXTRA_LARGE': self.content_extra_large_radio,
            'ORIGINAL': self.content_original_size_radio
        }

        self.sample_method_radio_dict = {
            'TOP': self.user_top_radio,
            'NEW': self.user_new_radio,
            'SELECTED_NEW': self.user_selected_new_radio
        }

        self.run_with_main_checkbox.setChecked(self.settings_manager.user_finder_run_with_main)
        self.auto_add_checkbox.setChecked(self.settings_manager.user_finder_auto_add_found)
        self.content_size_radio_dict[self.settings_manager.user_finder_preview_size].setChecked(True)
        self.show_reddit_page_checkbox.setChecked(self.settings_manager.user_finder_show_users_reddit_page)
        self.settings_manager.user_finder_show_users_reddit_page = self.show_reddit_page_checkbox.isChecked()
        self.sample_size_spinbox.setValue(self.settings_manager.user_finder_sample_size)
        self.sample_method_radio_dict[self.settings_manager.user_finder_sample_type_method].setChecked(True)

    def accept(self):
        self.save_settings()
        self.save_window_settings()
        super().accept()

    def closeEvent(self, QCloseEvent):
        self.save_window_settings()

    def save_settings(self):
        self.settings_manager.user_finder_run_with_main = self.run_with_main_checkbox.isChecked()
        self.settings_manager.user_finder_auto_add_found = self.auto_add_checkbox.isChecked()
        self.settings_manager.user_finder_auto_add_user_list = self.auto_add_user_list_combo.currentText()
        self.settings_manager.user_finder_sample_size = self.sample_size_spinbox.value()
        self.settings_manager.user_finder_sample_type_method = self.get_sample_method()
        self.settings_manager.user_finder_preview_size = self.get_content_preview_size()
        self.settings_manager.save_user_finder()

    def save_window_settings(self):
        self.settings_manager.user_finder_settings_gui_geom = self.saveGeometry()
        self.settings_manager.save_user_finder_settings_dialog()

    def get_content_preview_size(self):
        for key, value in self.content_size_radio_dict.items():
            if value.isChecked():
                return key
