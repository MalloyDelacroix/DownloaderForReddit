from PyQt5 import QtCore, QtWidgets, QtGui

from GUI_Resources.UserFinderGUI_auto import Ui_UserFinderGUI
from Core import Injector
from GUI.AddUserDialog import AddUserDialog
from GUI.UserFinderSettingsGUI import UserFinderSettingsGUI


class UserFinderGUI(QtWidgets.QWidget, Ui_UserFinderGUI):

    def __init__(self, user_view_chooser_dict):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.user_view_chooser_dict = user_view_chooser_dict
        self.running = False
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        self.view_users_button.clicked.connect(self.change_page)
        self.run_button.clicked.connect(self.run_user_finder)
        self.user_finder_button.clicked.connect(self.change_page)

        self.add_subreddit_button.clicked.connect(self.add_subreddit)
        self.remove_subreddit_button.clicked.connect(self.remove_subreddit)
        self.add_user_button.clicked.connect(self.add_user)
        self.remove_user_button.clicked.connect(self.remove_user)

        self.settings_manager = Injector.get_settings_manager()
        geom = self.settings_manager.user_finder_GUI_geom
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())
        self.splitter_one.restoreState(self.settings_manager.user_finder_splitter_one_state)
        self.splitter_two.restoreState(self.settings_manager.user_finder_splitter_two_state)
        self.splitter_three.restoreState(self.settings_manager.user_finder_splitter_three_state)

        if 'filler' in self.settings_manager.user_finder_subreddit_list:
            self.settings_manager.user_finder_subreddit_list.remove('filler')
        if 'filler' in self.settings_manager.user_finder_user_blacklist:
            self.settings_manager.user_finder_user_blacklist.remove('filler')

        for item in self.settings_manager.user_finder_subreddit_list:
            self.subreddit_watchlist_widget.addItem(item)

        for item in self.settings_manager.user_finder_blacklist:
            self.user_blacklist_widget.addItem(item)

        self.top_sort_radio_dict = {
            'HOUR': self.hour_radio,
            'DAY': self.day_radio,
            'WEEK': self.week_radio,
            'MONTH': self.month_radio,
            'YEAR': self.year_radio,
            'ALL': self.all_time_radio
        }

        if len(self.user_view_chooser_dict) > 0:
            self.auto_add_user_list_combo.addItems(self.user_view_chooser_dict.keys())
        else:
            self.auto_add_user_list_combo.addItem('No User List Available')

        self.top_sort_radio_dict[self.settings_manager.user_finder_top_sort_method].setChecked(True)
        self.filter_by_score_checkbox.setChecked(self.settings_manager.user_finder_filter_by_score)
        self.score_limit_spinbox.setValue(self.settings_manager.user_finder_score_limit)
        # TODO: Figure out how to set the auto user list combo from settings

        self.subreddit_watchlist_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subreddit_watchlist_widget.customContextMenuRequested.connect(self.subreddit_watchlist_right_click)

        self.user_blacklist_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.user_blacklist_widget.customContextMenuRequested.connect(self.user_blacklist_right_click)

        self.user_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.user_list_view.customContextMenuRequested.connect(self.user_list_right_click)

        self.content_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.content_list_widget.customContextMenuRequested.connect(self.content_list_right_click)

    def change_page(self):
        self.stacked_widget.setCurrentIndex(1 if self.stacked_widget.currentIndex() == 0 else 0)

    def subreddit_watchlist_right_click(self):
        pass

    def user_blacklist_right_click(self):
        pass

    def add_subreddit(self):
        dialog = AddUserDialog()
        dialog.add_another_button.clicked.connect(lambda: self.add_subreddit_to_list(dialog.name))
        dialog.show()
        reply = dialog.exec_()
        if reply == QtWidgets.QDialog.Accepted:
            self.add_subreddit_to_list(dialog.name)

    def add_subreddit_to_list(self, subreddit):
        if subreddit != '' and subreddit != ' ' and subreddit not in self.subreddit_watchlist_widget.items():
            self.subreddit_watchlist_widget.addItem(subreddit)

    def remove_subreddit(self):
        self.subreddit_watchlist_widget.takeItem(self.subreddit_watchlist_widget.currentIndex())

    def add_user(self):
        dialog = AddUserDialog()
        dialog.add_another_button.clicked.connect(lambda: self.add_user_to_blacklist(dialog.name))
        dialog.show()
        reply = dialog.exec_()
        if reply == QtWidgets.QDialog.Accepted:
            self.add_user_to_blacklist(dialog.name)

    def add_user_to_blacklist(self, user):
        if user != '' and user != ' ' and user not in self.user_blacklist_widget.items():
            self.user_blacklist_widget.addItem(user)

    def remove_user(self):
        self.user_blacklist_widget.takeItem(self.user_blacklist_widget.currentIndex())

    def user_list_right_click(self):
        pass

    def content_list_right_click(self):
        pass

    def run_user_finder(self):
        pass

    def accept(self):
        pass

    def open_user_finder_settings(self):
        dialog = UserFinderSettingsGUI()
        dialog.show()
        dialog.exec_()

    def save_settings(self):
        self.settings_manager.user_finder_top_sort_method = self.get_top_sort_method()
        self.settings_manager.user_finder_filter_by_score = self.filter_by_score_checkbox.isChecked()
        self.settings_manager.user_finder_score_limit = self.score_limit_spinbox.value()
        self.settings_manager.user_finder_subreddit_list = [x for x in self.subreddit_watchlist_widget.items()]
        self.settings_manager.user_finder_user_blacklist = [x for x in self.user_blacklist_widget.items()]

    def get_top_sort_method(self):
        for key, value in self.top_sort_radio_dict.items():
            if value.isChecked():
                return key

    def get_sample_method(self):
        for key, value in self.sample_method_radio_dict.items():
            if value.isChecked():
                return key

    def save_window_settings(self):
        self.settings_manager.user_finder_GUI_geom = self.saveGeometry()
        self.settings_manager.user_finder_splitter_one_state = self.splitter_one.saveState()
        self.settings_manager.user_finder_splitter_two_state = self.splitter_two.saveState()
        self.settings_manager.user_finder_splitter_three_state = self.splitter_three.saveState()

















































