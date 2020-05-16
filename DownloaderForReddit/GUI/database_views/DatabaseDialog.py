import logging
from PyQt5.QtWidgets import QMenu, QActionGroup, QWidget, QInputDialog
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor

from DownloaderForReddit.Database.Models import DownloadSession, RedditObject, Post, Content, Comment
from DownloaderForReddit.Database.Filters import (DownloadSessionFilter, RedditObjectListFilter, RedditObjectFilter,
                                                  PostFilter, CommentFilter, ContentFilter)
from DownloaderForReddit.GUI.BlankDialog import BlankDialog
from DownloaderForReddit.GUI_Resources.database_views.DatabaseDialog_auto import Ui_DatabaseDialog
from DownloaderForReddit.ViewModels.DownloadSessionViewModels import (DownloadSessionModel, RedditObjectModel,
                                                                      PostTableModel, ContentListModel,
                                                                      CommentTreeModel)
from DownloaderForReddit.Utils import Injector, SystemUtil
from .FilterWidget import FilterWidget


def hold_setup(method):
    def set_hold(instance):
        instance.hold_setup = True
        method(instance)
        instance.hold_setup = False
    return set_hold


def check_hold(method):
    def check(instance, **kwargs):
        if not instance.hold_setup or kwargs.pop('override_hold', False):
            method(instance, **kwargs)
    return check


class DatabaseDialog(QWidget, Ui_DatabaseDialog):

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()
        self.hold_setup = False

        self.setup_call_list = []

        geom = self.settings_manager.database_view_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.splitter.setSizes(self.settings_manager.database_view_splitter_position)

        self.filter = FilterWidget()

        self.show_download_sessions_checkbox.setChecked(self.settings_manager.database_view_show_download_sessions)
        self.show_reddit_objects_checkbox.setChecked(self.settings_manager.database_view_show_reddit_objects)
        self.show_posts_checkbox.setChecked(self.settings_manager.database_view_show_posts)
        self.show_content_checkbox.setChecked(self.settings_manager.database_view_show_content)
        self.show_comments_checkbox.setChecked(self.settings_manager.database_view_show_comments)

        for x in DownloadSessionFilter.get_order_fields():
            self.download_session_sort_combo.addItem(x.replace('_', ' ').title(), x)
        for x in RedditObjectFilter.get_order_fields():
            self.reddit_object_sort_combo.addItem(x.replace('_', ' ').title(), x)
        for x in PostFilter.get_order_fields():
            self.post_sort_combo.addItem(x.replace('_', ' ').title(), x)
        for x in ContentFilter.get_order_fields():
            self.content_sort_combo.addItem(x.replace('_', ' ').title(), x)
        for x in CommentFilter.get_order_fields():
            self.comment_sort_combo.addItem(x.replace('_', ' ').title(), x)

        self.download_session_sort_combo.setCurrentText(
            self.settings_manager.database_view_download_session_order.replace('_', ' ').title())
        self.reddit_object_sort_combo.setCurrentText(
            self.settings_manager.database_view_reddit_object_order.replace('_', ' ').title())
        self.post_sort_combo.setCurrentText(
            self.settings_manager.database_view_post_order.replace('_', ' ').title())
        self.content_sort_combo.setCurrentText(
            self.settings_manager.database_view_content_order.replace('_', ' ').title())
        self.comment_sort_combo.setCurrentText(
            self.settings_manager.database_view_comment_order.replace('_', ' ').title())

        self.download_session_desc_sort_checkbox.setChecked(
            self.settings_manager.database_view_download_session_desc_order)
        self.reddit_object_desc_sort_checkbox.setChecked(
            self.settings_manager.database_view_reddit_object_desc_order)
        self.post_desc_sort_checkbox.setChecked(self.settings_manager.database_view_post_desc_order)
        self.content_desc_sort_checkbox.setChecked(self.settings_manager.database_view_content_desc_order)
        self.comment_desc_sort_checkbox.setChecked(self.settings_manager.database_view_comment_desc_order)

        self.download_session_sort_combo.currentIndexChanged.connect(self.change_download_session_sort)
        self.reddit_object_sort_combo.currentIndexChanged.connect(self.change_reddit_object_sort)
        self.post_sort_combo.currentIndexChanged.connect(self.change_post_sort)
        self.content_sort_combo.currentIndexChanged.connect(self.change_content_sort)
        self.comment_sort_combo.currentIndexChanged.connect(self.change_comment_sort)

        self.download_session_desc_sort_checkbox.toggled.connect(self.change_download_session_sort)
        self.reddit_object_desc_sort_checkbox.toggled.connect(self.change_reddit_object_sort)
        self.post_desc_sort_checkbox.toggled.connect(self.change_post_sort)
        self.content_desc_sort_checkbox.toggled.connect(self.change_content_sort)
        self.comment_desc_sort_checkbox.toggled.connect(self.change_comment_sort)

        self.icon_size = self.settings_manager.database_view_icon_size

        self.current_download_session = None
        self.current_reddit_object = None
        self.current_post = None
        self.current_content = None
        self.current_comment = None

        self.download_session_model = DownloadSessionModel()
        self.download_session_list_view.setModel(self.download_session_model)

        self.reddit_object_model = RedditObjectModel()
        self.reddit_object_list_view.setModel(self.reddit_object_model)

        self.post_model = PostTableModel()
        self.post_table_view.setModel(self.post_model)

        self.set_content_icon_size()
        self.content_model = ContentListModel()
        self.content_list_view.setModel(self.content_model)
        self.content_list_view.setBatchSize(2)

        self.comment_tree_model = CommentTreeModel()
        self.comment_tree_view.setModel(self.comment_tree_model)
        self.comment_tree_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.reddit_object_widget.setVisible(self.show_reddit_objects_checkbox.isChecked())
        self.post_widget.setVisible(self.show_posts_checkbox.isChecked())
        self.content_widget.setVisible(self.show_content_checkbox.isChecked())
        self.comment_widget.setVisible(self.show_comments_checkbox.isChecked())

        self.post_text_browser.setVisible(False)
        self.post_text_browser.attach_signal.connect(self.attach_post_text_browser)
        self.post_text_browser.detach_signal.connect(self.detach_post_text_browser)

        self.comment_text_browser.setVisible(False)
        self.comment_text_browser.attach_signal.connect(self.attach_comment_text_browser)
        self.comment_text_browser.detach_signal.connect(self.detach_comment_text_browser)

        self.show_reddit_objects_checkbox.stateChanged.connect(self.toggle_reddit_object_view)
        self.show_posts_checkbox.stateChanged.connect(self.toggle_post_view)
        self.show_content_checkbox.stateChanged.connect(self.toggle_content_view)
        self.show_comments_checkbox.stateChanged.connect(self.toggle_comment_view)

        self.download_session_list_view.selectionModel().selectionChanged.connect(self.set_current_download_session)
        self.reddit_object_list_view.selectionModel().selectionChanged.connect(self.set_current_reddit_object)
        self.post_table_view.selectionModel().selectionChanged.connect(self.set_current_post)
        self.content_list_view.selectionModel().selectionChanged.connect(self.set_current_content)
        self.comment_tree_view.selectionModel().selectionChanged.connect(self.set_current_comment)

        self.content_list_view.doubleClicked.connect(self.open_selected_content)

        self.download_session_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.download_session_list_view.customContextMenuRequested.connect(self.download_session_view_context_menu)

        post_headers = self.post_table_view.horizontalHeader()
        post_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        post_headers.customContextMenuRequested.connect(self.post_headers_context_menu)
        post_headers.setSectionsMovable(True)
        for key, value in self.settings_manager.database_view_post_table_headers.items():
            index = self.post_model.headers.index(key)
            post_headers.setSectionHidden(index, not value)

        self.content_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_list_view.customContextMenuRequested.connect(self.content_view_context_menu)

        comment_headers = self.comment_tree_view.header()
        comment_headers.setSectionsMovable(True)
        comment_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        comment_headers.customContextMenuRequested.connect(self.comment_header_context_menu)
        for key, value in self.settings_manager.database_view_comment_tree_headers.items():
            index = self.comment_tree_model.headers.index(key)
            comment_headers.setSectionHidden(index, not value)

        self.download_session_focus_radio.toggled.connect(lambda x: self.setup_download_sessions() if x else None)
        self.reddit_object_focus_radio.toggled.connect(lambda x: self.setup_reddit_objects() if x else None)
        self.post_focus_radio.toggled.connect(lambda x: self.setup_posts() if x else None)
        self.content_focus_radio.toggled.connect(lambda x: self.setup_content() if x else None)
        self.comment_focus_radio.toggled.connect(lambda x: self.setup_comments() if x else None)
        self.focus_map = {
            'DOWNLOAD_SESSION': self.download_session_focus_radio,
            'REDDIT_OBJECT': self.reddit_object_focus_radio,
            'POST': self.post_focus_radio,
            'CONTENT': self.content_focus_radio,
            'COMMENT': self.comment_focus_radio
        }
        self.focus_map[self.settings_manager.database_view_focus_model].setChecked(True)

        self.download_session_list_view.verticalScrollBar().valueChanged.connect(lambda: self.monitor_scrollbar(
            self.download_session_list_view.verticalScrollBar(), self.download_session_model,
            self.set_download_session_data
        ))
        self.reddit_object_list_view.verticalScrollBar().valueChanged.connect(lambda: self.monitor_scrollbar(
            self.reddit_object_list_view.verticalScrollBar(), self.reddit_object_model, self.set_reddit_object_data
        ))
        self.post_table_view.verticalScrollBar().valueChanged.connect(lambda: self.monitor_scrollbar(
            self.post_table_view.verticalScrollBar(), self.post_model, self.set_post_data
        ))
        self.content_list_view.verticalScrollBar().valueChanged.connect(lambda: self.monitor_scrollbar(
            self.content_list_view.verticalScrollBar(), self.content_model, self.set_content_data, 80
        ))

    def check_call_list(self, call):
        contains = call in self.setup_call_list
        if not contains:
            self.setup_call_list.append(call)
        return contains

    @property
    def cascade(self):
        return len(self.setup_call_list) == 0

    @property
    def download_session_focus(self):
        return self.download_session_focus_radio.isChecked()

    @property
    def reddit_object_focus(self):
        return self.reddit_object_focus_radio.isChecked()

    @property
    def post_focus(self):
        return self.post_focus_radio.isChecked()

    @property
    def content_focus(self):
        return self.content_focus_radio.isChecked()

    @property
    def comment_focus(self):
        return self.comment_focus_radio.isChecked()

    @property
    def show_download_sessions(self):
        return self.show_download_sessions_checkbox.isChecked()

    @property
    def show_reddit_objects(self):
        return self.show_reddit_objects_checkbox.isChecked()

    @property
    def show_posts(self):
        return self.show_posts_checkbox.isChecked()

    @property
    def show_content(self):
        return self.show_content_checkbox.isChecked()

    @property
    def show_comments(self):
        return self.show_comments_checkbox.isChecked()

    @property
    def download_session_order(self):
        return self.download_session_sort_combo.currentData(Qt.UserRole)

    @property
    def download_session_desc(self):
        return self.download_session_desc_sort_checkbox.isChecked()

    @property
    def reddit_object_order(self):
        return self.reddit_object_sort_combo.currentData(Qt.UserRole)

    @property
    def reddit_object_desc(self):
        return self.reddit_object_desc_sort_checkbox.isChecked()

    @property
    def post_order(self):
        return self.post_sort_combo.currentData(Qt.UserRole)

    @property
    def post_desc(self):
        return self.post_desc_sort_checkbox.isChecked()

    @property
    def comment_order(self):
        return self.comment_sort_combo.currentData(Qt.UserRole)

    @property
    def comment_desc(self):
        return self.comment_desc_sort_checkbox.isChecked()

    @property
    def content_order(self):
        return self.content_sort_combo.currentData(Qt.UserRole)

    @property
    def content_desc(self):
        return self.content_desc_sort_checkbox.isChecked()

    @property
    def current_download_session_id(self):
        try:
            return self.current_download_session.id
        except AttributeError:
            return None

    @property
    def current_reddit_object_id(self):
        try:
            return self.current_reddit_object.id
        except AttributeError:
            return None

    @property
    def current_post_id(self):
        try:
            return self.current_post.id
        except AttributeError:
            return None

    @property
    def current_content_id(self):
        try:
            return self.current_content.id
        except AttributeError:
            return None

    @property
    def current_comment_id(self):
        try:
            return self.current_comment.id
        except AttributeError:
            return None

    def download_session_view_context_menu(self):
        menu = QMenu()
        try:
            dl_session = \
                self.download_session_model.get_item(self.download_session_list_view.selectedIndexes()[0].row())
        except:
            dl_session = None
        rename = menu.addAction('Rename Session', lambda: self.rename_download_session(dl_session))
        rename.setDisabled(dl_session is None)
        menu.exec_(QCursor.pos())

    def post_headers_context_menu(self):
        menu = QMenu()
        for value in self.post_model.headers:
            item = menu.addAction(value.replace('_', ' ').replace(' display', '').title())
            item.triggered.connect(lambda x, header=value: self.toggle_post_table_header(header))
            item.setCheckable(True)
            item.setChecked(self.settings_manager.database_view_post_table_headers[value])
        menu.exec_(QCursor.pos())

    def attach_post_text_browser(self):
        self.post_text_splitter.addWidget(self.post_text_browser)
        self.post_text_browser.stand_alone = False

    def detach_post_text_browser(self):
        dialog = BlankDialog(parent=self)
        dialog.add_widgets(self.post_text_browser)
        dialog.closing.connect(self.post_text_browser.handle_dialog_movement)
        dialog.setWhatsThis('Displays the text from the selected post.  Close dialog to re-attach text box.')
        dialog.show()
        self.post_text_browser.stand_alone = True

    def attach_comment_text_browser(self):
        self.comment_text_splitter.addWidget(self.comment_text_browser)
        self.comment_text_browser.stand_alone = False

    def detach_comment_text_browser(self):
        dialog = BlankDialog(parent=self)
        dialog.add_widgets(self.comment_text_browser)
        dialog.closing.connect(self.comment_text_browser.handle_dialog_movement)
        dialog.setWhatsThis('Displays the text from the selected comment.  Close dialog to re-attach text box.')
        dialog.show()
        self.comment_text_browser.stand_alone = True

    def toggle_post_table_header(self, header):
        index = self.post_model.headers.index(header)
        visible = self.settings_manager.database_view_post_table_headers[header]
        self.settings_manager.database_view_post_table_headers[header] = not visible
        # sets the table header visibility to the opposite of what visible originally was
        self.post_table_view.horizontalHeader().setSectionHidden(index, visible)

    def content_view_context_menu(self):
        menu = QMenu()
        try:
            content = self.content_model.get_item(self.content_list_view.selectedIndexes()[0].row())
        except:
            content = None

        open_directory = menu.addAction('Open Directory', lambda: SystemUtil.open_in_system(content.directory_path))
        open_directory.setDisabled(content is None)

        icon_menu = QMenu('Icon Size')
        action_group = QActionGroup(self)
        extra_small_item = self.add_icon_menu_item(icon_menu, action_group, 'Extra Small', 72)
        small_item = self.add_icon_menu_item(icon_menu, action_group, 'Small', 110)
        medium_item = self.add_icon_menu_item(icon_menu, action_group, 'Medium', 176)
        large_item = self.add_icon_menu_item(icon_menu, action_group, 'Large', 256)
        extra_large_item = self.add_icon_menu_item(icon_menu, action_group, 'Extra Large', 420)
        custom_item = self.add_icon_menu_item(icon_menu, action_group, 'Custom', None, connect=False)
        custom_item.triggered.connect(self.set_custom_content_icon_size)
        if not any(x.isChecked() for x in icon_menu.actions()):
            custom_item.setChecked(True)
            custom_item.setText(custom_item.text() + f' ({self.icon_size})')
        menu.addMenu(icon_menu)

        menu.exec_(QCursor.pos())

    def add_icon_menu_item(self, icon_menu, action_group, text, icon_size, connect=True):
        if connect:
            item = icon_menu.addAction(text, lambda: self.set_content_icon_size(icon_size))
        else:
            item = icon_menu.addAction(text)
        item.setCheckable(True)
        item.setChecked(icon_size == self.icon_size)
        action_group.addAction(item)
        return item

    def comment_header_context_menu(self):
        menu = QMenu()
        for value in self.comment_tree_model.headers:
            item = menu.addAction(value.replace('_', ' ').title())
            item.triggered.connect(lambda x, header=value: self.toggle_comment_tree_headers(header))
            item.setCheckable(True)
            item.setChecked(self.settings_manager.database_view_comment_tree_headers[value])
        menu.exec_(QCursor.pos())

    def toggle_comment_tree_headers(self, header):
        index = self.comment_tree_model.headers.index(header)
        visible = self.settings_manager.database_view_comment_tree_headers[header]
        self.settings_manager.database_view_comment_tree_headers[header] = not visible
        # sets the header visibility to the opposite of what it originally was
        self.comment_tree_view.header().setSectionHidden(index, visible)

    def toggle_reddit_object_view(self):
        if self.show_reddit_objects_checkbox.isChecked():
            self.reddit_object_widget.setVisible(True)
            self.setup_reddit_objects()
        else:
            self.reddit_object_widget.setVisible(False)
            if self.show_posts_checkbox.isChecked():
                self.setup_posts()
            else:
                self.setup_content()

    def toggle_post_view(self):
        if self.show_posts_checkbox.isChecked():
            self.post_widget.setVisible(True)
            self.setup_posts()
        else:
            self.post_widget.setVisible(False)
            self.set_content_data()

    def toggle_content_view(self):
        self.set_content_data()
        self.content_widget.setVisible(self.show_content_checkbox.isChecked())

    def toggle_comment_view(self):
        self.set_comment_data()
        self.comment_widget.setVisible(self.show_comments_checkbox.isChecked())

    @hold_setup
    def change_download_session_sort(self):
        self.set_download_session_data(override_hold=True)
        self.download_session_list_view.setCurrentIndex(
            self.download_session_model.get_item_index(self.current_download_session))
        self.settings_manager.database_view_download_session_order = \
            self.download_session_sort_combo.currentData(Qt.UserRole)

    @hold_setup
    def change_reddit_object_sort(self):
        self.set_reddit_object_data(override_hold=True)
        self.reddit_object_list_view.setCurrentIndex(
            self.reddit_object_model.get_item_index(self.current_reddit_object))
        self.settings_manager.database_view_reddit_object_order = \
            self.reddit_object_sort_combo.currentData(Qt.UserRole)

    @hold_setup
    def change_post_sort(self):
        self.set_post_data(override_hold=True)
        self.reddit_object_list_view.setCurrentIndex(self.post_model.get_item_index(self.current_post))
        self.settings_manager.database_view_post_order = self.post_sort_combo.currentData(Qt.UserRole)

    @hold_setup
    def change_content_sort(self):
        self.set_content_data(override_hold=True)
        self.content_list_view.setCurrentIndex(self.content_model.get_item_index(self.current_content))
        self.settings_manager.database_view_content_order = self.content_sort_combo.currentData(Qt.UserRole)

    @hold_setup
    def change_comment_sort(self):
        # TODO: figure out how best to order this
        self.settings_manager.database_view_comment_order = self.comment_sort_combo.currentData(Qt.UserRole)

    def set_content_icon_size(self, size=None):
        if size is None:
            size = self.icon_size
        else:
            self.icon_size = size
        self.content_list_view.setIconSize(QSize(size, size))
        self.content_list_view.setGridSize(QSize(size + 2, size + 45))

    def set_custom_content_icon_size(self):
        size, ok = QInputDialog.getInt(self, 'Custom Icon Size', 'Enter custom icon size:')
        if ok:
            self.set_content_icon_size(size)

    def open_selected_content(self):
        content = self.content_model.get_item(self.content_list_view.selectedIndexes()[0].row())
        SystemUtil.open_in_system(content.get_full_file_path())

    def rename_download_session(self, dl_session):
        if dl_session is not None:
            new_name, ok = QInputDialog.getText(self, 'New Session Name', 'Enter new session name:')
            if ok:
                dl_session.name = new_name
                self.session.commit()
                self.download_session_model.refresh()

    def setup_download_sessions(self):
        self.set_download_session_data()
        self.set_first_download_session_index()

    def setup_reddit_objects(self):
        self.set_reddit_object_data()
        self.set_first_reddit_object_index()

    def setup_posts(self):
        self.set_post_data()
        self.set_first_post_index()

    def setup_content(self):
        self.set_content_data()
        self.set_first_content_index()

    def setup_comments(self):
        self.set_comment_data()
        self.set_first_comment_index()

    def cascade_setup(self):
        if not self.download_session_focus and not self.check_call_list('DOWNLOAD_SESSION'):
            self.setup_download_sessions()
        if not self.reddit_object_focus and not self.check_call_list('REDDIT_OBJECT'):
            self.setup_reddit_objects()
        if not self.post_focus and not self.check_call_list('POST'):
            self.setup_posts()
        if not self.content_focus and not self.check_call_list('CONTENT'):
            self.setup_content()
        if not self.comment_focus and not self.check_call_list('COMMENT'):
            self.setup_comments()

    def set_current_download_session(self):
        if self.show_download_sessions:
            try:
                self.current_download_session = \
                    self.download_session_model.get_item(self.download_session_list_view.currentIndex().row())
            except IndexError:
                self.current_download_session = None
            if self.cascade:
                self.setup_call_list.append('DOWNLOAD_SESSION')
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_reddit_object(self):
        if self.show_reddit_objects:
            try:
                self.current_reddit_object = \
                    self.reddit_object_model.get_item(self.reddit_object_list_view.currentIndex().row())
            except IndexError:
                self.current_reddit_object = None
            if self.cascade:
                self.setup_call_list.append('REDDIT_OBJECT')
                if not self.reddit_object_focus:
                    self.setup_call_list.append('DOWNLOAD_SESSION')
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_post(self):
        if self.show_posts:
            try:
                self.current_post = self.post_model.get_item(self.post_table_view.currentIndex().row())
                if self.current_post.text_html is not None and self.current_post.text_html != '':
                    self.post_text_browser.setVisible(True)
                    self.post_text_browser.setHtml(self.current_post.text_html)
                else:
                    if not self.post_text_browser.stand_alone and self.post_text_browser.isVisible():
                        self.post_text_browser.setVisible(False)
                    self.post_text_browser.clear()
            except IndexError:
                self.current_post = None
            if self.cascade:
                self.setup_call_list.append('POST')
                if not self.post_focus:
                    self.setup_call_list.extend(['DOWNLOAD_SESSION', 'REDDIT_OBJECT'])
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_content(self):
        if self.show_content:
            try:
                self.current_content = self.content_model.get_item(self.content_list_view.currentIndex().row())
            except IndexError:
                self.current_content = None
            if self.cascade:
                self.setup_call_list.append('CONTENT')
                if not self.content_focus:
                    self.setup_call_list.extend(['DOWNLOAD_SESSION', 'REDDIT_OBJECT', 'POST'])
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_comment(self):
        if self.show_comments:
            try:
                self.current_comment = self.comment_tree_model.get_item(self.comment_tree_view.currentIndex())
                if self.current_comment.body_html is not None and self.current_comment.body_html != '':
                    self.comment_text_browser.setVisible(True)
                    self.comment_text_browser.setHtml(self.current_comment.body_html)
                else:
                    if not self.comment_text_browser.stand_alone and self.comment_text_browser.isVisible():
                        self.comment_text_browser.setVisible(False)
                    self.comment_text_browser.clear()
            except (IndexError, AttributeError):
                self.current_comment = None
                self.comment_text_browser.setVisible(False)
                self.comment_text_browser.clear()
            if self.cascade:
                self.setup_call_list.append('COMMENT')
                if not self.comment_focus:
                    self.setup_call_list.extend(['DOWNLOAD_SESSION', 'REDDIT_OBJECT', 'POST', 'COMMENT'])
                self.cascade_setup()
                self.setup_call_list.clear()

    @check_hold
    def set_download_session_data(self, extend=False):
        f = DownloadSessionFilter()
        filter_tups = self.filter.filter(DownloadSession)
        query = self.session.query(DownloadSession)
        if self.reddit_object_focus:
            dl_ids = self.session.query(Post.download_session_id)\
                .filter(Post.significant_reddit_object_id == self.current_reddit_object_id)
            query = query.filter(DownloadSession.id.in_(dl_ids))
        elif self.post_focus:
            query = query.filter(DownloadSession.id == self.current_post.download_session_id)
        elif self.content_focus:
            query = query.filter(DownloadSession.id == self.current_content.download_session_id)
        elif self.comment_focus:
            query = query.filter(DownloadSession.id == self.current_comment.download_session_id)
        final_query = f.filter(self.session, *filter_tups, query=query, order_by=self.download_session_order,
                                desc=self.download_session_desc)
        if not extend:
            self.download_session_model.set_data(final_query)
        else:
            self.download_session_model.load_next_page(final_query)

    @check_hold
    def set_reddit_object_data(self, extend=False):
        f = RedditObjectFilter()
        filter_tups = self.filter.filter(RedditObject)
        query = self.session.query(RedditObject).filter(RedditObject.significant == True)
        if self.download_session_focus:
            subquery = self.session.query(Post.significant_reddit_object_id)\
                .filter(Post.download_session_id == self.current_download_session_id)
            query = query.filter(RedditObject.id.in_(subquery))
        elif self.post_focus:
            query = query.filter(RedditObject.id == self.current_post.significant_reddit_object_id)
        elif self.content_focus:
            query = query.filter(RedditObject.id == self.current_content.post.significant_reddit_object_id)
        elif self.comment_focus:
            query = query.filter(RedditObject.id == self.current_comment.post.significant_reddit_object_id)
        final_query = f.filter(self.session, *filter_tups, query=query, order_by=self.reddit_object_order,
                               desc=self.reddit_object_desc)
        if not extend:
            self.reddit_object_model.set_data(final_query)
        else:
            self.reddit_object_model.load_next_page(final_query)

    @check_hold
    def set_post_data(self, extend=False):
        f = PostFilter()
        filter_tups = self.filter.filter(Post)
        query = self.session.query(Post)
        if self.download_session_focus or self.reddit_object_focus:
            if self.show_download_sessions:
                query = query.filter(Post.download_session_id == self.current_download_session_id)
            if self.show_reddit_objects:
                query = query.filter(Post.significant_reddit_object_id == self.current_reddit_object_id)
        elif self.content_focus:
            query = query.filter(Post.id == self.current_content.post_id)
        elif self.comment_focus:
            query = query.filter(Post.id == self.current_comment.post_id)
        final_query = f.filter(self.session, *filter_tups, query=query, order_by=self.post_order,
                               desc=self.post_desc)
        if not extend:
            self.post_model.set_data(final_query)
        else:
            self.post_model.load_next_page(final_query)

    @check_hold
    def set_content_data(self, extend=False):
        f = ContentFilter()
        filter_tups = self.filter.filter(Content)
        query = self.session.query(Content)
        if self.download_session_focus:
            query = query.filter(Content.download_session_id == self.current_download_session_id)
            if self.show_posts:
                query = query.filter(Content.post_id == self.current_post_id)
            elif self.show_reddit_objects:
                posts = self.session.query(Post.id) \
                    .filter(Post.significant_reddit_object_id == self.current_reddit_object_id)
                query = query.filter(Content.post_id.in_(posts))
        elif self.reddit_object_focus:
            posts = self.session.query(Post.id) \
                .filter(Post.significant_reddit_object_id == self.current_reddit_object_id)
            query = query.filter(Content.post_id.in_(posts))
            if self.show_posts:
                query = query.filter(Content.post_id == self.current_post_id)
            elif self.show_download_sessions:
                query = query.filter(Content.download_session_id == self.current_download_session_id)
        elif self.post_focus:
            query = query.filter(Content.post_id == self.current_post_id)
        elif self.comment_focus:
            query = query.filter(Content.comment_id == self.current_comment)
        final_query = f.filter(self.session, *filter_tups, query=query, order_by=self.content_order,
                               desc=self.content_desc)
        if not extend:
            self.content_model.set_data(final_query)
        else:
            self.content_model.load_next_page(final_query)

    @check_hold
    def set_comment_data(self, extend=False):
        f = CommentFilter()
        filter_tups = self.filter.filter(Comment)
        query = self.session.query(Comment)
        if self.download_session_focus or self.reddit_object_focus:
            if self.show_posts:
                query = query.filter(Comment.post_id == self.current_post_id)
            elif self.show_reddit_objects:
                posts = self.session.query(Post.id)\
                    .filter(Post.significant_reddit_object_id == self.current_reddit_object_id)
                query = query.filter(Comment.post_id.in_(posts))
            else:
                query = query.filter(Comment.download_session_id == self.current_download_session_id)
        elif self.post_focus:
            query = query.filter(Comment.post_id == self.current_post_id)
        elif self.content_focus:
            query = query.filter(Comment.post_id == self.current_content.comment_id)
        final_query = f.filter(self.session, *filter_tups, query=query, order_by=self.comment_order,
                               desc=self.comment_desc)
        if not extend:
            self.comment_tree_model.set_data(final_query)
        else:
            self.comment_tree_model.load_next_page(query)

    def set_first_download_session_index(self):
        if not self.download_session_model.contains(self.current_download_session):
            first_index = self.download_session_model.createIndex(0, 0)
            if self.download_session_list_view.currentIndex() != first_index:
                self.download_session_list_view.setCurrentIndex(first_index)
            else:
                self.set_current_download_session()

    def set_first_reddit_object_index(self):
        if not self.reddit_object_model.contains(self.current_reddit_object):
            first_index = self.reddit_object_model.createIndex(0, 0)
            if self.reddit_object_list_view.currentIndex() != first_index:
                self.reddit_object_list_view.setCurrentIndex(first_index)
            else:
                self.set_current_reddit_object()

    def set_first_post_index(self):
        if not self.post_model.contains(self.current_post):
            first_index = self.post_model.createIndex(0, 0)
            if self.post_table_view.currentIndex() != first_index:
                self.post_table_view.setCurrentIndex(first_index)
            else:
                self.set_current_post()

    def set_first_content_index(self):
        if not self.content_model.contains(self.current_content):
            first_index = self.content_model.createIndex(0, 0)
            if self.content_list_view.currentIndex() != first_index:
                self.content_list_view.setCurrentIndex(first_index)
            else:
                self.set_current_content()

    def set_first_comment_index(self):
        if not self.comment_tree_model.contains(self.current_comment):
            first_index = self.comment_tree_model.get_first_index()
            if self.comment_tree_view.currentIndex() != first_index:
                self.comment_tree_view.setCurrentIndex(first_index)
            else:
                self.set_current_comment()

    def monitor_scrollbar(self, bar, model, load_method, load_percentage=90):
        value = bar.value()
        p = (value / bar.maximum()) * 100
        if p >= load_percentage and model.has_next_page and not model.loading:
            load_method(extend=True)

    def closeEvent(self, event):
        self.settings_manager.database_view_geom['width'] = self.width()
        self.settings_manager.database_view_geom['height'] = self.height()
        self.settings_manager.database_view_geom['x'] = self.x()
        self.settings_manager.database_view_geom['y'] = self.y()
        self.settings_manager.database_view_splitter_position = self.splitter.sizes()
        self.settings_manager.database_view_icon_size = self.icon_size
        for key, value in self.focus_map.items():
            if value.isChecked():
                self.settings_manager.database_view_focus_model = key
                break
        self.settings_manager.database_view_show_download_sessions = self.show_download_sessions
        self.settings_manager.database_view_show_reddit_objects = self.show_reddit_objects
        self.settings_manager.database_view_show_posts = self.show_posts
        self.settings_manager.database_view_show_content = self.show_content
        self.settings_manager.database_view_show_comments = self.show_comments
        self.settings_manager.database_view_download_session_order = self.download_session_order
        self.settings_manager.database_view_reddit_object_order = self.reddit_object_order
        self.settings_manager.database_view_post_order = self.post_order
        self.settings_manager.database_view_content_order = self.content_order
        self.settings_manager.database_view_comment_order = self.comment_order
        self.settings_manager.database_view_download_session_desc_order = self.download_session_desc
        self.settings_manager.database_view_reddit_object_desc_order = self.reddit_object_desc
        self.settings_manager.database_view_post_desc_order = self.post_desc
        self.settings_manager.database_view_content_desc_order = self.content_desc
        self.settings_manager.database_view_comment_desc_order = self.comment_desc
        super().closeEvent(event)
