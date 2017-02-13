"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


import os
import sys
import subprocess
import datetime
import time
import re
from PyQt5 import QtWidgets, QtCore, QtGui

from SubredditSettingsDialog_auto import Ui_subreddit_settings_dialog
from Messages import Message


class SubredditSettingsDialog(QtWidgets.QDialog, Ui_subreddit_settings_dialog):

    single_download = QtCore.pyqtSignal(object)

    def __init__(self, list_model, clicked_sub):
        """
        Class that forms the subreddit dialog box that is accessed by right-clicking a subreddit in the GUI window to
        adjust settings for individual subreddits.  Also contains a list model of all other subreddits in the same list
        so other subreddits can be selected without having to exit the dialog.

        :param list_model: The underlying list model that is currently displayed in the GUI
        :param clicked_sub: The subreddit name that is right-clicked to bring the menu up.
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.subreddit_list = list_model.reddit_object_list
        self.display_list = [x.name for x in self.subreddit_list]
        self.current_sub = clicked_sub
        self.restore_defaults = False
        self.closed = False

        self.settings = QtCore.QSettings('SomeGuySoftware', 'RedditDownloader')

        self.subreddit_content_icons_full_width = self.settings.value('subreddit_content_icons_full_width', False,
                                                                      type=bool)
        self.subreddit_content_icon_size = self.settings.value('subreddit_content_icon_size', 110, type=int)

        self.download_subreddit_button.clicked.connect(self.download_single)
        self.view_downloads_button.clicked.connect(self.change_page)
        self.view_downloads_button.setToolTip('This will only display the downloaded subreddit content if it is located'
                                              ' <br>in the subreddit folder')
        self.view_downloads_button.setToolTipDuration(-1)

        self.cust_save_path_dialog.clicked.connect(self.select_save_path_dialog)

        for sub in self.display_list:
            self.subreddit_list_widget.addItem(sub)
        self.subreddit_list_widget.setCurrentRow(self.display_list.index(self.current_sub.name))
        self.subreddit_list_widget.currentRowChanged.connect(self.list_item_change)

        self.save_cancel_buton_box.accepted.connect(self.accept)
        self.save_cancel_buton_box.rejected.connect(self.close)
        self.restore_defaults_button.clicked.connect(self.set_restore_defaults)

        self.name_downloads_combo.addItems(('Image/Album Id', 'Post Title'))
        self.save_by_method_combo.addItems(('Subreddit Name', 'User Name', 'Subreddit Name/User Name',
                                            'User Name/Subreddit Name'))
        self.sub_sort_combo.addItems(('New', 'Hot', 'Rising', 'Controversial', 'Top - Hour', 'Top - Day', 'Top - Week',
                                      'Top - Month', 'Top - Year', 'Top - All'))

        self.previous_download_list.acceptRichText()
        self.previous_download_list.setOpenExternalLinks(True)

        self.setup()

        self.page_one_geom = None
        self.page_two_geom = None

        self.subreddit_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subreddit_list_widget.customContextMenuRequested.connect(self.subreddit_list_widget_right_click)

        self.subreddit_content_list.setViewMode(QtWidgets.QListView.IconMode)
        self.subreddit_content_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.subreddit_content_list.customContextMenuRequested.connect(self.subreddit_content_list_right_click)
        self.subreddit_content_list.doubleClicked.connect(lambda:
                                                          self.open_file(self.subreddit_content_list.currentRow()))

    def setup(self):
        """
        Sets up parts of the dialog that are dependant upon which subreddit is selected.  It is used as an independent
        function instead of in __init__ because as different subs are selected from the sub list, these items need to
        be reset and applied to the newly selected sub
        """
        self.previous_download_list.clear()
        for item in self.current_sub.already_downloaded:
            self.previous_download_list.append('<a style="color:black;" href=%s>%s</a>' % (item, item))

        self.name_downloads_combo.setCurrentText(self.current_sub.name_downloads_by)

        self.do_not_edit_checkbox.setChecked(self.current_sub.do_not_edit)
        date_limit = self.current_sub.date_limit if self.current_sub.custom_date_limit is None else \
            self.current_sub.custom_date_limit
        if self.current_sub.custom_date_limit is None:
            self.restrict_date_checkbox.setChecked(False)
        else:
            self.restrict_date_checkbox.setChecked(True)

        self.date_limit_edit.setDateTime(datetime.datetime.fromtimestamp(date_limit))
        self.post_limit_spinbox.setValue(self.current_sub.post_limit)
        self.custom_save_path_line_edit.setText(self.current_sub.save_path)
        self.download_videos_checkbox.setChecked(self.current_sub.download_videos)
        self.download_images_checkbox.setChecked(self.current_sub.download_images)
        self.avoid_duplicates_checkbox.setChecked(self.current_sub.avoid_duplicates)
        self.sub_added_label.setText('Subreddit Added On: %s' % datetime.date.strftime(datetime.datetime.fromtimestamp(
                                     self.current_sub.user_added), '%m-%d-%Y at %I:%M %p'))
        self.subreddit_downloads_label.setText(str(len(self.current_sub.already_downloaded)))

    def list_item_change(self):
        self.save_temporary_sub()
        self.current_sub = self.subreddit_list[self.subreddit_list_widget.currentRow()]
        self.setup()
        if self.stacked_widget.currentIndex() == 1:
            self.setup_subreddit_content_list()

    def save_temporary_sub(self):
        """
        Saves changes made to the subreddit list contained in this settings dialog which is a copy of the subreddit list
        in the main GUI window.  This is done to preserve changes when switching subs in dialog list so that if one sub
        is changed and then switched to another sub, if the user clicks "OK", changes to all subs will be saved
        """
        self.current_sub.do_not_edit = self.do_not_edit_checkbox.isChecked()
        if self.current_sub.date_limit != int(time.mktime(time.strptime(self.date_limit_edit.text(),
                                                                        '%m/%d/%Y %I:%M %p'))):
            self.current_sub.custom_date_limit = int(time.mktime(time.strptime(self.date_limit_edit.text(),
                                                                               '%m/%d/%Y %I:%M %p')))
        elif not self.restrict_date_checkbox.isChecked():
            self.current_sub.custom_date_limit = 1
        self.current_sub.post_limit = self.post_limit_spinbox.value()
        self.current_sub.name_downloads_by = self.name_downloads_combo.currentText()
        self.current_sub.save_path = '%s%s' % (self.custom_save_path_line_edit.text(), '/' if
                                               not self.custom_save_path_line_edit.text().endswith('/') else '')
        self.current_sub.download_videos = self.download_videos_checkbox.isChecked()
        self.current_sub.download_images = self.download_images_checkbox.isChecked()
        self.current_sub.avoid_duplicates = self.avoid_duplicates_checkbox.isChecked()

    def download_single(self):
        """
        Downloads only the subreddit that is selected.  Emits a signal picked up by the main GUI that runs an instance
        of the RedditExtractor class with a single item subreddit list
        """
        self.download_subreddit_button.setText("Downloading...")
        self.download_subreddit_button.setDisabled(False)
        self.save_temporary_sub()
        self.single_download.emit(self.current_sub)

    def select_save_path_dialog(self):
        path = self.custom_save_path_line_edit.text() if self.custom_save_path_line_edit != '' else \
                   '%s%s' % (os.path.expanduser('~'), '/Downloads/')
        folder_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Save Folder', path))
        if folder_name != '':
            self.custom_save_path_line_edit.setText(folder_name + '/')

    def set_restore_defaults(self):
        self.restore_defaults = True

    def accept(self):
        self.save_temporary_sub()
        super().accept()

    def change_page(self):
        if self.stacked_widget.currentIndex() == 0:
            self.page_one_geom = (self.width(), self.height())
            self.change_to_downloads_view()
        else:
            self.page_two_geom = (self.width(), self.height())
            self.change_to_sub_settings()

    def change_to_downloads_view(self):
        """
        Changes some settings dialog GUI options that are not relevent to the download page and also changes the page to
        show the downloaded content
        """
        if self.page_two_geom is not None:
            self.resize(self.page_two_geom[0], self.page_two_geom[1])
        self.stacked_widget.setCurrentIndex(1)
        self.view_downloads_button.setText('Sub Settings')
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')
        self.setup_subreddit_content_list()
        self.view_downloads_button.setToolTip('Show settings for selected subreddit')

    def change_to_sub_settings(self):
        """
        Changes GUI options that are not relevent to the settings window and also changes the page to show the user
        settings
        """
        if self.page_one_geom is not None:
            self.resize(self.page_one_geom[0], self.page_one_geom[1])
        self.stacked_widget.setCurrentIndex(0)
        self.view_downloads_button.setText('View Downloads')
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(True)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Cancel')
        self.view_downloads_button.setToolTip('This will only display the downloaded subreddit content if it is located'
                                              ' <br>in the subreddit folder. Content saved with the method "User Name"'
                                              ' <br>or "User Name/Subreddit Name" cannot be displayed')

    def setup_subreddit_content_list(self):
        """Sets up the subreddit content list with content that is in the currently selected subreddits directory"""
        self.subreddit_content_list.clear()
        try:
            folder_name = '%s%s/' % (self.current_sub.save_path, self.current_sub.name.lower())
            self.picture_list = self.extract_pictures(folder_name)
            if len(self.picture_list) > 0:
                for file in self.picture_list:
                    path, text = file.rsplit('/', 1)
                    item = QtWidgets.QListWidgetItem()
                    icon = QtGui.QIcon()
                    pixmap = QtGui.QPixmap(file).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)
                    icon.addPixmap(pixmap)
                    item.setIcon(icon)
                    item.setText(text)
                    self.subreddit_content_list.addItem(item)
                    QtWidgets.QApplication.processEvents()

        except FileNotFoundError:
            self.subreddit_content_list.addItem('No content has been downloaded for this subreddit yet')

    def extract_pictures(self, main_folder):
        """
        This is implemented because depending on the subreddit save method there may be multiple folders named after
        the posting user located in the subreddits save directory. This method extracts all pictures from the save
        directory and its subdirectories
        """
        main_folder = main_folder + '/' if not main_folder.endswith('/') else main_folder
        self.pictures = [os.path.join(main_folder, x) for x in os.listdir(main_folder) if
                    os.path.isfile(os.path.join(main_folder, x)) and x.lower().endswith(('.jpg', '.jpeg', '.png'))]
        sub_folders = [x for x in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, x))]

        for folder in sub_folders:
            path = os.path.join(main_folder, folder)
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)) and file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.pictures.append('%s%s%s' % (path, '/' if not path.endswith('/') else '', file))
        return sorted(self.pictures, key=alphanum_key)

    def subreddit_list_widget_right_click(self):
        menu = QtWidgets.QMenu()
        try:
            position = self.subreddit_list_widget.currentRow()
            open_sub_folder = menu.addAction('Open Subreddit Download Folder')
            open_sub_folder.triggered.connect(lambda: self.open_subreddit_download_folder(position))
        except FileNotFoundError:
            Message.no_subreddit_download_folder(self)
        menu.exec(QtGui.QCursor.pos())

    def subreddit_content_list_right_click(self):
        self.menu = QtWidgets.QMenu()
        try:
            position = self.subreddit_content_list.currentRow()
            open_file = self.menu.addAction('Open File')
            self.menu.addSeparator()
            self.icons_full_width = self.menu.addAction('Icons Full List Width')
            self.icons_full_width.setCheckable(True)
            self.icon_size_menu = self.menu.addMenu('Icon Size')
            self.icon_size_group = QtWidgets.QActionGroup(self)
            self.icon_size_group.setExclusive(True)

            self.icon_size_extra_small = self.icon_size_menu.addAction('Extra Small')
            self.icon_size_extra_small.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_extra_small)
            self.icon_size_small = self.icon_size_menu.addAction('Small')
            self.icon_size_small.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_small)
            self.icon_size_medium = self.icon_size_menu.addAction('Medium')
            self.icon_size_medium.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_medium)
            self.icon_size_large = self.icon_size_menu.addAction('Large')
            self.icon_size_large.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_large)
            self.icon_size_extra_large = self.icon_size_menu.addAction('Extra Large')
            self.icon_size_extra_large.setCheckable(True)
            self.icon_size_group.addAction(self.icon_size_extra_large)
            self.set_context_menu_items_checked()

            open_file.triggered.connect(lambda: self.open_file(position))
            self.icons_full_width.triggered.connect(self.set_icons_full_width)
            self.icon_size_extra_small.triggered.connect(lambda: self.set_icon_size(48))
            self.icon_size_small.triggered.connect(lambda: self.set_icon_size(72))
            self.icon_size_medium.triggered.connect(lambda: self.set_icon_size(110))
            self.icon_size_large.triggered.connect(lambda: self.set_icon_size(176))
            self.icon_size_extra_large.triggered.connect(lambda: self.set_icon_size(256))

        except AttributeError:
            print('SubredditSettingsDialog line 310')
        self.menu.exec(QtGui.QCursor.pos())

    def open_subreddit_download_folder(self, position):
        selected_sub = self.subreddit_list[position]
        sub_folder = '%s%s%s' % (selected_sub.save_path, '/' if not selected_sub.save_path.endswith('/') else '',
                                 selected_sub.name)

        try:
            if sys.platform == 'win32':
                os.startfile(sub_folder)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, sub_folder])
        except FileNotFoundError:
            Message.no_subreddit_download_folder(self)

    def open_file(self, position):
        if sys.platform == 'win32':
            os.startfile(self.picture_list[position])
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, self.picture_list[position]])

    def set_icons_full_width(self):
        self.subreddit_content_icons_full_width = True
        self.subreddit_content_list.setIconSize(QtCore.QSize(self.subreddit_content_list.width(),
                                                             self.subreddit_content_list.width()))

    def set_icon_size(self, size):
        self.subreddit_content_icons_full_width = False
        self.subreddit_content_icon_size = size
        self.subreddit_content_list.setIconSize(QtCore.QSize(size, size))

    def set_context_menu_items_checked(self):
        if self.subreddit_content_icons_full_width:
            self.icons_full_width.setChecked(True)
        else:
            self.icons_full_width.setChecked(False)
            if self.subreddit_content_icon_size == 48:
                self.icon_size_extra_small.setChecked(True)
            elif self.subreddit_content_icon_size == 72:
                self.icon_size_small.setChecked(True)
            elif self.subreddit_content_icon_size == 110:
                self.icon_size_medium.setChecked(True)
            elif self.subreddit_content_icon_size == 176:
                self.icon_size_large.setChecked(True)
            else:
                self.icon_size_extra_large.setChecked(True)

    def resizeEvent(self, event):
        if self.subreddit_content_icons_full_width:
            icon_size = self.subreddit_content_list.width()
        else:
            icon_size = self.subreddit_content_icon_size
        self.subreddit_content_list.setIconSize(QtCore.QSize(icon_size, icon_size))

    def closeEvent(self, event):
        self.closed = True
        self.settings.setValue('subreddit_content_icons_full_width', self.subreddit_content_icons_full_width)
        self.settings.setValue('subreddit_content_icon_size', self.subreddit_content_icon_size)


# Functions that sort the displayed content in an expected manner
def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]
