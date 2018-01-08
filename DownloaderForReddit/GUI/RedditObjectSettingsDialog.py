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


import datetime
import time
import copy
from PyQt5 import QtCore, QtWidgets, QtGui
import cv2

from GUI_Resources.RedditObjectSettingsDialog_auto import Ui_RedditObjectSettingsDialog
from Core import Injector
from Core.Messages import Message
from Core.AlphanumKey import ALPHANUM_KEY
from ViewModels.RedditObjectItemDisplayModel import RedditObjectItemDisplayModel
from Core.RedditObjects import *
from CustomWidgets.CustomListWidgetItem import CustomListItem
from Core import SystemUtil


class RedditObjectSettingsDialog(QtWidgets.QDialog, Ui_RedditObjectSettingsDialog):

    single_download = QtCore.pyqtSignal(object)

    def __init__(self, list_model, init_item, downloader_running):
        """
        Allows reddit object settings to be changed individually.
        :param list_model: The current list model that is being displayed in the main GUI window.
        :param init_item: The item that was clicked in order to bring this dialog up and the item who's settings will
                          first be displayed.
        :type list_model: ListModel or list
        :type init_item: RedditObject
        """
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.running = downloader_running
        try:
            self.object_list = list_model.reddit_object_list
        except AttributeError:
            self.object_list = list_model
        self.display_list = [x.name for x in self.object_list]
        self.current_object = init_item
        self.restore_defaults = False
        self.closed = False
        self.object_type = init_item.object_type

        if not self.running and len(self.current_object.content) <= 0:
            self.editing_disabled_label.setVisible(False)
            self.current_temp_object = copy.deepcopy(self.current_object)
        else:
            self.current_temp_object = None
            self.set_edit_disabled()
        self.temp_object_dict = {}

        self.settings_manager = Injector.get_settings_manager()
        geom = self.settings_manager.reddit_object_settings_dialog_geom
        state = self.settings_manager.reddit_object_settings_dialog_splitter_state
        self.restoreGeometry(geom if geom is not None else self.saveGeometry())
        self.splitter.restoreState(state if state is not None else self.splitter.saveState())
        self.show_downloads = True

        if self.object_type == 'USER':
            self.sub_sort_label.setVisible(False)
            self.sub_sort_combo.setVisible(False)
            self.save_by_method_label.setVisible(False)
            self.save_by_method_combo.setVisible(False)
        else:
            self.save_by_method_combo.addItems(('Subreddit Name', 'User Name', 'Subreddit Name/User Name',
                                                'User Name/Subreddit Name'))
            self.sub_sort_combo.addItems(
                ('New', 'Hot', 'Rising', 'Controversial', 'Top - Hour', 'Top - Day', 'Top - Week',
                 'Top - Month', 'Top - Year', 'Top - All'))
            self.set_subreddit_sort_combo()

        self.nsfw_filter_combo.addItems(self.settings_manager.nsfw_filter_dict.keys())

        self.total_downloads_title_label.setText('Total %s Downloads:' % self.object_type_str)

        self.content_icons_full_width = self.settings_manager.reddit_object_content_icons_full_width
        self.content_icon_size = self.settings_manager.reddit_object_content_icon_size

        self.current_item_display = self.settings_manager.current_reddit_object_settings_item_display_list
        self.item_display_list_model = RedditObjectItemDisplayModel(self.current_object, self.current_item_display)
        self.item_display_list_view.setModel(self.item_display_list_model)

        self.download_object_button.clicked.connect(self.download_single)
        self.view_downloads_button.clicked.connect(self.change_page)

        for item in self.display_list:
            self.object_list_widget.addItem(item)
        self.object_list_widget.setCurrentRow(self.display_list.index(self.current_object.name))
        self.object_list_widget.currentRowChanged.connect(self.list_item_change)

        self.save_cancel_buton_box.accepted.connect(self.accept)
        self.save_cancel_buton_box.rejected.connect(self.close)
        self.restore_defaults_button.clicked.connect(self.set_restore_defaults)

        self.name_downloads_combo.addItems(('Image/Album Id', 'Post Title'))

        self.saved_content_name_dict = {}
        self.setup()

        self.page_one_geom = None
        self.page_two_geom = None

        self.restrict_date_checkbox.setToolTip('Right click to reset to %s date to last downloaded link date' %
                                               self.object_type_str)

        self.object_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.object_list_widget.customContextMenuRequested.connect(self.object_list_right_click)
        self.object_list_widget.doubleClicked.connect(lambda: self.open_item_download_folder(
                                                      self.object_list_widget.currentRow()))

        self.content_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.content_list.customContextMenuRequested.connect(self.content_list_right_click)
        self.content_list.doubleClicked.connect(self.open_file)

        self.item_display_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.item_display_list_view.customContextMenuRequested.connect(self.item_display_list_right_click)

        self.restrict_date_checkbox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.restrict_date_checkbox.customContextMenuRequested.connect(self.date_right_click)

        self.date_limit_edit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.date_limit_edit.customContextMenuRequested.connect(self.date_right_click)

        self.save_by_method_combo.currentIndexChanged.connect(self.set_save_path_name_label)

    @property
    def object_type_str(self):
        """Returns a string of the object type with the first letter capitalized to be used in displays."""
        return self.object_type[0] + self.object_type[1:].lower()

    def set_subreddit_sort_combo(self):
        """
        Sets the current text in the sub_sort_combo depending on the subreddit sort method and subreddit sort top
        methods in the settings manager
        """
        if self.settings_manager.subreddit_sort_method != 'TOP':
            self.sub_sort_combo.setCurrentText(self.settings_manager.subreddit_sort_method.title())
        else:
            sort_dict = {
                'DAY': 'Top - Day',
                'WEEK': 'Top - Week',
                'MONTH': 'Top - Month',
                'YEAR': 'Top - Year',
                'ALL': 'Top - All'
            }
            self.sub_sort_combo.setCurrentText(sort_dict[self.settings_manager.subreddit_sort_top_method])

    def set_edit_disabled(self):
        self.download_object_button.setEnabled(False)
        self.do_not_edit_checkbox.setEnabled(False)
        self.sub_sort_combo.setEnabled(False)
        self.restrict_date_checkbox.setEnabled(False)
        self.date_limit_edit.setEnabled(False)
        self.post_limit_spinbox.setEnabled(False)
        self.name_downloads_combo.setEnabled(False)
        self.save_by_method_combo.setEnabled(False)
        self.custom_save_path_dialog.setEnabled(False)
        self.custom_save_path_line_edit.setEnabled(False)
        self.download_videos_checkbox.setEnabled(False)
        self.download_images_checkbox.setEnabled(False)
        self.avoid_duplicates_checkbox.setEnabled(False)
        self.nsfw_filter_combo.setEnabled(False)
        self.restore_defaults_button.setEnabled(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def setup(self):
        """Sets up each part of the settings dialog for the current reddit object."""
        if self.current_temp_object:
            self.set_temp_object()
            self.setup_display(self.current_temp_object)
        else:
            self.setup_display(self.current_object)

    def set_temp_object(self):
        if self.current_object.name in self.temp_object_dict:
            self.current_temp_object = self.temp_object_dict[self.current_object.name]
        else:
            self.current_temp_object = copy.deepcopy(self.current_object)

    def setup_display(self, reddit_object):
        self.do_not_edit_checkbox.setChecked(reddit_object.do_not_edit)
        self.restrict_date_checkbox.setChecked(reddit_object.custom_date_limit != 1)
        self.post_limit_spinbox.setValue(reddit_object.post_limit)
        self.name_downloads_combo.setCurrentText(reddit_object.name_downloads_by)
        self.custom_save_path_line_edit.setText(reddit_object.save_path)
        self.set_save_path_name_label()
        self.download_videos_checkbox.setChecked(reddit_object.download_videos)
        self.download_images_checkbox.setChecked(reddit_object.download_images)
        self.avoid_duplicates_checkbox.setChecked(reddit_object.avoid_duplicates)
        self.set_nsfw_filter_combo(reddit_object)
        self.total_downloads_label.setText(str(reddit_object.number_of_downloads))
        added_on = datetime.date.strftime(datetime.datetime.fromtimestamp(reddit_object.user_added),
                                          '%m-%d-%Y at %I:%M %p')
        self.item_added_label.setText('%s Added On: %s' % (self.object_type_str, added_on))
        if self.object_type == 'SUBREDDIT':
            self.save_by_method_combo.setCurrentText(reddit_object.subreddit_save_method)
        self.item_display_list_model.reddit_object = reddit_object
        self.setup_item_display_list(self.current_item_display)
        self.set_date_display(reddit_object)

    def set_save_path_name_label(self):
        self.save_path_name_label.setText(self.get_name_label_text())
        self.setup_save_path_tooltips()

    def get_name_label_text(self):
        slash = '/' if not self.custom_save_path_line_edit.text().endswith('/') else ''
        if self.object_type == 'USER':
            return '%s%s/' % (slash, self.current_object.name)
        else:
            sub_method = self.save_by_method_combo.currentText()
            if sub_method == 'Subreddit Name':
                return '%s%s/' % (slash, self.current_object.name)
            elif sub_method == 'User Name':
                return '%s<User>/' % slash
            elif sub_method == 'Subreddit Name/User Name':
                return '%s%s/<User>/' % (slash, self.current_object.name)
            else:
                return '%s<User>/%s' % (slash, self.current_object.name)

    def setup_save_path_tooltips(self):
        tooltip = '%s%s' % (self.custom_save_path_line_edit.text(), self.save_path_name_label.text())
        self.custom_save_path_line_edit.setToolTip(tooltip)
        self.save_path_name_label.setToolTip(tooltip)

    def set_nsfw_filter_combo(self, reddit_object):
        for key, value in self.settings_manager.nsfw_filter_dict.items():
            if reddit_object.nsfw_filter == value:
                self.nsfw_filter_combo.setCurrentText(key)
                break

    def set_date_display(self, reddit_object):
        """Sets the date display box.  This is a separate method so it can be called from other class methods."""
        date_limit = reddit_object.custom_date_limit if reddit_object.custom_date_limit is not \
                                                                   None else reddit_object.date_limit
        if date_limit < 86400:
            date_limit = 86400
        self.date_limit_edit.setDateTime(datetime.datetime.fromtimestamp(date_limit))

    def setup_item_display_list(self, display_type):
        """
        Sets up the display list that displays a reddit objects previous downloads, saved submissions, and saved
        content.
        """
        display_dict = {'previous_downloads': 'Previous Downloads:', 'saved_submissions': 'Saved Submissions:',
                        'saved_content': 'Saved Content:'}
        self.current_item_display = display_type
        self.item_display_list_model.display_list = display_type
        self.item_display_list_model.refresh()
        self.item_display_list_label.setText(display_dict[display_type])

    def remove_selected(self):
        """Removes the selected display item from the display list and the reddit objects corresponding item list."""
        index_list = [x.row() for x in self.item_display_list_view.selectedIndexes()]
        self.item_display_list_model.removeRows(index_list)

    def list_item_change(self):
        """Changes the displayed reddit object list."""
        if self.current_temp_object:
            self.save_temp_object()
        self.current_object = self.object_list[self.object_list_widget.currentRow()]
        self.setup()
        if self.stacked_widget.currentIndex() == 1:
            self.setup_content_list()

    def save_temp_object(self):
        """
        Saves changes made to the current reddit object when the current reddit object is changed.  This allows for a
        new reddit object to be displayed and changed while preserving the changes made to the current object but also
        making these changes permanent until the save button is clicked.
        """
        self.current_temp_object.do_not_edit = self.do_not_edit_checkbox.isChecked()
        if self.current_temp_object.date_limit != int(time.mktime(time.strptime(self.date_limit_edit.text(),
                                                                                '%m/%d/%Y %I:%M %p'))):
            self.current_temp_object.custom_date_limit = int(time.mktime(time.strptime(self.date_limit_edit.text(),
                                                                                       '%m/%d/%Y %I:%M %p')))
        if not self.restrict_date_checkbox.isChecked():
            self.current_temp_object.custom_date_limit = 1
        self.current_temp_object.post_limit = self.post_limit_spinbox.value()
        self.current_temp_object.name_downloads_by = self.name_downloads_combo.currentText()
        self.current_temp_object.save_path = self.custom_save_path_line_edit.text()
        if not self.current_temp_object.save_path.endswith('/'):
            self.current_temp_object.save_path += '/'
        self.current_temp_object.download_videos = self.download_videos_checkbox.isChecked()
        self.current_temp_object.download_images = self.download_images_checkbox.isChecked()
        self.current_temp_object.avoid_duplicates = self.avoid_duplicates_checkbox.isChecked()
        self.current_temp_object.nsfw_filter = \
            self.settings_manager.nsfw_filter_dict[self.nsfw_filter_combo.currentText()]
        if self.object_type == 'SUBREDDIT':
            self.current_temp_object.subreddit_save_method = self.save_by_method_combo.currentText()
        self.temp_object_dict[self.current_temp_object.name] = self.current_temp_object

    def download_single(self):
        """Downloads only the current reddit object."""
        self.download_object_button.setText('Downloading...')
        self.download_object_button.setDisabled(True)
        self.save_temp_object()
        self.single_download.emit(self.current_temp_object)

    def select_save_path_dialog(self):
        """Opens a dialog to choose a directory path to be set as the objects save path."""
        if self.custom_save_path_line_edit.text() != '':
            path = self.custom_save_path_line_edit.text()
        else:
            path = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Save Folder', path))
        if folder_name != '' and folder_name is not None:
            self.custom_save_path_line_edit.setText(folder_name + '/')

    def set_restore_defaults(self):
        self.restore_defaults = True

    def change_page(self):
        """Calls the appropriate method to change the page based on the current page."""
        if self.stacked_widget.currentIndex() == 0:
            self.page_one_geom = (self.width(), self.height())
            self.change_to_downloads_view()
        else:
            self.page_two_geom = (self.width(), self.height())
            self.change_to_settings_view()

    def change_to_downloads_view(self):
        """Changes the stacked widget to the downloads page and sets up the content view."""
        if self.page_two_geom is not None:
            self.resize(self.page_two_geom[0], self.page_two_geom[1])
        self.stacked_widget.setCurrentIndex(1)
        self.view_downloads_button.setText('%s Settings' % self.object_type_str)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(False)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Close')
        self.setup_content_list()

    def change_to_settings_view(self):
        """Changes the stacked widget to the downloads page and calls the setup method."""
        if self.page_one_geom is not None:
            self.resize(self.page_one_geom[0], self.page_two_geom[1])
        self.stacked_widget.setCurrentIndex(0)
        self.view_downloads_button.setText('View Downloads')
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Ok).setVisible(True)
        self.save_cancel_buton_box.button(QtWidgets.QDialogButtonBox.Cancel).setText('Cancel')

    def setup_content_list(self):
        """Sets up the content list based on the current selected users save path."""
        self.content_list.clear()
        if self.content_icons_full_width:
            icon_size = self.content_list.width()
        else:
            icon_size = self.content_icon_size
        self.content_list.setIconSize(QtCore.QSize(icon_size, icon_size))
        if self.show_downloads:
            try:
                self.current_download_folder = self.get_download_folder()
                if len(self.current_download_folder) > 0:
                    self.display_content()
            except FileNotFoundError:
                self.content_list.addItem('No content has been downloaded for this %s yet' % self.object_type.lower())
            except:
                print('Exception in setup content list')

    def get_download_folder(self):
        """Returns a list of file objects to be displayed in the content view."""
        if self.object_type == 'USER':
            save_path = self.current_object.save_directory
            return sorted([os.path.join(save_path, x) for x in os.listdir(save_path) if
                           os.path.isfile(os.path.join(save_path, x))], key=ALPHANUM_KEY)
        else:
            file_list = self.extract_files_from_sub_folder(os.path.join(self.current_object.save_directory,
                                                                        self.current_object.name.lower()))
            return sorted(file_list, key=ALPHANUM_KEY)

    def extract_files_from_sub_folder(self, folder):
        """Gathers all files from the supplied path and all sub folders."""
        file_list = []
        for item in os.listdir(folder):
            file = os.path.join(folder, item)
            if os.path.isfile(file):
                file_list.append(file)
            elif os.path.isdir(file):
                file_list.extend(self.extract_files_from_sub_folder(file))
        return file_list

    def display_content(self):
        """Sets up a list item for each file in the content folder and adds it to the content display view."""
        for file in self.current_download_folder:
            try:
                text = file.rsplit('/', 1)[1]
                item = CustomListItem()
                item.path = file
                icon = self.make_icon(file)
                if icon:
                    item.setIcon(icon)
                item.setText(text)
                self.content_list.addItem(item)
                QtWidgets.QApplication.processEvents()
            except:
                print('Could not display content')

    def make_icon(self, file):
        """
        Makes an icon out of the supplied file. If the file is of gif, webm, or mp4 format, the icon is created based on
        the gif display type settings in the settings manager.
        :param file: The image or animation file that is to be made into an icon.
        :type file: str
        :return: The icon object to be displayed
        :rtype: QtGui.QIcon
        """
        icon = QtGui.QIcon()
        if not file.endswith(('webm', 'gif', 'mp4')):
            pixmap = self.make_pixmap(file)
        else:
            if self.settings_manager.gif_display_method == 'FRAME':
                pixmap = self.get_frame(file)
            elif self.settings_manager.gif_display_method == 'PLACEHOLDER':
                pixmap = self.make_pixmap('Images/gif_placeholder.jpg')
            else:
                return None
        icon.addPixmap(pixmap)
        return icon

    def make_pixmap(self, file):
        """Createsa pixmap out of the supplied file with a uniform size and options."""
        return QtGui.QPixmap(file).scaled(QtCore.QSize(500, 500), QtCore.Qt.KeepAspectRatio)

    def get_frame(self, file):
        """
        Gets the first frame from an animated file to be displayed as an icon.
        :param file: The animated file from which the frame is to be taken.
        :return: A pixmap of the frame.
        """
        vid = cv2.VideoCapture(file)
        ret, frame = vid.read()
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        return self.make_pixmap(img)

    def object_list_right_click(self):
        """Displays a context menu for the object list."""
        menu = QtWidgets.QMenu()
        try:
            position = self.object_list_widget.currentRow()
            open_download_folder = menu.addAction('Open Download Folder')
            open_download_folder.triggered.connect(lambda: self.open_item_download_folder(position))
        except AttributeError:
            pass
        menu.exec_(QtGui.QCursor.pos())

    def item_display_list_right_click(self):
        """Displays a context menu for the item display list."""
        menu = QtWidgets.QMenu()
        remove_text = '%s' % 'Remove Items' if len(self.item_display_list_view.selectedIndexes()) > 2 else 'Remove Item'
        open_link = menu.addAction('Open Link')
        remove_item = menu.addAction(remove_text)
        menu.addSeparator()
        previous_download_list = menu.addAction('Previous Downloads')
        saved_content_list = menu.addAction('Saved Content')
        saved_submissions_list = menu.addAction('Saved Submissions')
        menu_dict = {'previous_downloads': previous_download_list,
                     'saved_content': saved_content_list,
                     'saved_submissions': saved_submissions_list}
        open_link.triggered.connect(self.open_link)
        remove_item.triggered.connect(self.remove_selected)
        previous_download_list.triggered.connect(lambda: self.setup_item_display_list('previous_downloads'))
        saved_content_list.triggered.connect(lambda: self.setup_item_display_list('saved_content'))
        saved_submissions_list.triggered.connect(lambda: self.setup_item_display_list('saved_submissions'))
        open_link.setEnabled(self.current_item_display == 'previous_downloads')
        menu_dict[self.current_item_display].setEnabled(False)
        menu.exec_(QtGui.QCursor.pos())

    def content_list_right_click(self):
        """Displays a context menu for the content list."""
        menu = QtWidgets.QMenu()
        try:
            position = self.content_list.currentRow()
            open_file = menu.addAction('Open File')
            menu.addSeparator()
            icons_full_width = menu.addAction('Icons Full List Width')
            icons_full_width.setCheckable(True)
            icon_size_menu = menu.addMenu('Icon Size')
            icon_size_group = QtWidgets.QActionGroup(self)
            icon_size_group.setExclusive(True)

            icon_size_extra_small = icon_size_menu.addAction('Extra Small')
            icon_size_extra_small.setCheckable(True)
            icon_size_group.addAction(icon_size_extra_small)
            icon_size_small = icon_size_menu.addAction('Small')
            icon_size_small.setCheckable(True)
            icon_size_group.addAction(icon_size_small)
            icon_size_medium = icon_size_menu.addAction('Medium')
            icon_size_medium.setCheckable(True)
            icon_size_group.addAction(icon_size_medium)
            icon_size_large = icon_size_menu.addAction('Large')
            icon_size_large.setCheckable(True)
            icon_size_group.addAction(icon_size_large)
            icon_size_extra_large = icon_size_menu.addAction('Extra Large')
            icon_size_extra_large.setCheckable(True)
            icon_size_group.addAction(icon_size_extra_large)

            check_dict = {
                48: icon_size_extra_small,
                72: icon_size_small,
                110: icon_size_medium,
                176: icon_size_large,
                256: icon_size_extra_large
            }

            if self.content_icons_full_width:
                icons_full_width.setChecked(True)
            else:
                icons_full_width.setChecked(False)
                check_dict[self.content_icon_size].setChecked(True)

            open_file.triggered.connect(self.open_file)
            icons_full_width.triggered.connect(self.set_icons_full_width)
            icon_size_extra_small.triggered.connect(lambda: self.set_icon_size(48))
            icon_size_small.triggered.connect(lambda: self.set_icon_size(72))
            icon_size_medium.triggered.connect(lambda: self.set_icon_size(110))
            icon_size_large.triggered.connect(lambda: self.set_icon_size(176))
            icon_size_extra_large.triggered.connect(lambda: self.set_icon_size(256))

        except AttributeError:
            print('UserSettingsDialog AttributeError: user_content_right_click')
        menu.exec(QtGui.QCursor.pos())

    def date_right_click(self):
        """Displays a context menu for the date items."""
        menu = QtWidgets.QMenu()
        reset_date = menu.addAction('Reset Date')
        set_date_to_now = menu.addAction('Set Date To Now')
        reset_date.triggered.connect(self.reset_date)
        set_date_to_now.triggered.connect(self.set_date_to_now)
        menu.exec_(QtGui.QCursor.pos())

    def open_item_download_folder(self, position):
        """Opens the selected items download folder."""
        selected_object = self.object_list[position]
        path = self.get_download_folder_path(selected_object)
        try:
            SystemUtil.open_in_system(path)
        except AttributeError:
            print('Selected object has no attribute save_directory')
        except FileNotFoundError:
            Message.no_download_folder(self, self.object_type)

    def get_download_folder_path(self, reddit_object):
        """
        Returns the download folder path for the supplied reddit object based on object type and if the object is a
        subreddit, the subreddit save method.
        :param reddit_object: A reddit object (user or subreddit) for which a download folder path is needed.
        :type reddit_object: RedditObject
        :return: The path to the supplied objects download folder.
        :rtype: str
        """
        if reddit_object.object_type == 'SUBREDDIT':
            if self.save_by_method_combo.currentText().startswith('Subreddit'):
                return os.path.join(reddit_object.save_directory, reddit_object.name)
        return reddit_object.save_directory

    def open_file(self):
        """
        Selects a file based on the currently selected list item, and calls the method to open it in the file system.
        """
        file = self.content_list.currentItem().path
        try:
            SystemUtil.open_in_system(file)
        except AttributeError:
            print('Selected file has no attribute path')
        except FileNotFoundError:
            print('Cannot find file')

    def open_link(self):
        """Opens a link from the 'previous_downloads' list in the default web browser."""
        if self.current_item_display == 'previous_downloads':
            link = self.current_object.previous_downloads[self.item_display_list_view.currentIndex().row()]
            SystemUtil.open_in_system(link)

    def set_icons_full_width(self):
        self.content_icons_full_width = True
        self.content_list.setIconSize(QtCore.QSize(self.content_list.width(), self.content_list.width()))

    def set_icon_size(self, size):
        self.content_icons_full_width = False
        self.content_icon_size = size
        self.content_list.setIconSize(QtCore.QSize(size, size))

    def reset_date(self):
        self.current_temp_object.custom_date_limit = None
        self.set_date_display()

    def set_date_to_now(self):
        self.current_temp_object.custom_date_limit = datetime.datetime.now().timestamp()
        self.set_date_display()

    def resizeEvent(self, event):
        if self.content_icons_full_width:
            self.content_list.setIconSize(QtCore.QSize(self.content_list.width(), self.content_list.width()))

    def accept(self):
        self.save_temp_object()
        self.sub_temp_objects()
        super().accept()

    def closeEvent(self, event):
        self.closed = True
        self.settings_manager.reddit_object_settings_dialog_geom = self.saveGeometry()
        self.settings_manager.reddit_object_settings_dialog_splitter_state = self.splitter.saveState()
        self.settings_manager.reddit_object_content_icons_full_width = self.content_icons_full_width
        self.settings_manager.reddit_object_content_icon_size = self.content_icon_size
        self.settings_manager.current_reddit_object_settings_item_display_list = self.current_item_display
        self.settings_manager.save_reddit_object_settings_dialog()

    def sub_temp_objects(self):
        """
        Iterates through the object list and checks each name for existence in the temp_object_dict.  If a match is
        found, the object is replaced with the temporary object which will hold the changes that have been made through
        this dialog.
        """
        for x in range(len(self.object_list)):
            name = self.object_list[x].name
            try:
                self.object_list[x] = self.temp_object_dict[name]
            except KeyError:
                pass
