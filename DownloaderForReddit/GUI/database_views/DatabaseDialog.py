import logging
from PyQt5.QtWidgets import (QMenu, QWidgetAction, QInputDialog, QFontComboBox, QComboBox, QActionGroup,
                             QWidget, QHBoxLayout, QLabel)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QFont

from DownloaderForReddit.Database.Models import DownloadSession, RedditObject, Post, Content, Comment
from DownloaderForReddit.Database.Filters import (DownloadSessionFilter, RedditObjectListFilter, RedditObjectFilter,
                                                  PostFilter, CommentFilter, ContentFilter)
from DownloaderForReddit.GUI_Resources.database_views.DatabaseDialog_auto import Ui_DatabaseDialog
from DownloaderForReddit.ViewModels.DownloadSessionViewModels import (DownloadSessionModel, RedditObjectModel,
                                                                      PostTableModel, ContentListModel,
                                                                      CommentTreeModel)
from DownloaderForReddit.Utils import Injector, SystemUtil
from .FilterWidget import FilterWidget


class DatabaseDialog(QWidget, Ui_DatabaseDialog):

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()

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

        self.post_text_font_size = self.settings_manager.database_view_post_text_font_size
        self.post_text_font = QFont(self.settings_manager.database_view_post_text_font, self.post_text_font_size)
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

        self.comment_tree_model = CommentTreeModel()
        self.comment_tree_view.setModel(self.comment_tree_model)

        self.reddit_object_widget.setVisible(self.show_reddit_objects_checkbox.isChecked())
        self.post_widget.setVisible(self.show_posts_checkbox.isChecked())
        self.content_widget.setVisible(self.show_content_checkbox.isChecked())
        self.comment_widget.setVisible(self.show_comments_checkbox.isChecked())

        self.post_text_browser.setVisible(False)
        font = QFont(self.settings_manager.database_view_post_text_font,
                     self.settings_manager.database_view_post_text_font_size)
        self.post_text_browser.setFont(font)

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

        self.post_text_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.post_text_browser.customContextMenuRequested.connect(self.post_text_browser_context_menu)

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
    def reddit_object_order(self):
        return self.reddit_object_sort_combo.currentData(Qt.UserRole)

    @property
    def post_order(self):
        return self.post_sort_combo.currentData(Qt.UserRole)

    @property
    def comment_order(self):
        return self.comment_sort_combo.currentData(Qt.UserRole)

    @property
    def content_order(self):
        return self.content_sort_combo.currentData(Qt.UserRole)

    def download_session_view_context_menu(self):
        menu = QMenu()
        try:
            dl_session = \
                self.download_session_model.sessions[self.download_session_list_view.selectedIndexes()[0].row()]
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

    def toggle_post_table_header(self, header):
        index = self.post_model.headers.index(header)
        visible = self.settings_manager.database_view_post_table_headers[header]
        self.settings_manager.database_view_post_table_headers[header] = not visible
        # sets the table header visibility to the opposite of what visible originally was
        self.post_table_view.horizontalHeader().setSectionHidden(index, visible)

    def post_text_browser_context_menu(self):
        menu = QMenu()
        font_box = QFontComboBox()
        font_box.setCurrentFont(self.post_text_font)
        font_box.currentFontChanged.connect(lambda: self.set_post_text_font(font=font_box.currentFont()))
        font_box.currentFontChanged.connect(menu.close)
        font_box_label = QLabel('Font:')
        layout = QHBoxLayout()
        layout.addWidget(font_box_label)
        layout.addWidget(font_box)
        font_box_widget = QWidget(self)
        font_box_widget.setLayout(layout)
        font_box_item = QWidgetAction(self)
        font_box_item.setDefaultWidget(font_box_widget)

        font_size_box = QComboBox()
        font_size_box.addItems(str(x) for x in range(4, 30))
        font_size_box.setCurrentText(str(self.post_text_font_size))
        font_size_label = QLabel('Font Size:')
        size_layout = QHBoxLayout()
        size_layout.addWidget(font_size_label)
        size_layout.addWidget(font_size_box)
        font_size_widget = QWidget(self)
        font_size_widget.setLayout(size_layout)
        font_size_box.currentIndexChanged.connect(lambda:
                                                  self.set_post_text_font(size=int(font_size_box.currentText())))
        font_size_box.currentIndexChanged.connect(menu.close)
        font_size_item = QWidgetAction(self)
        font_size_item.setDefaultWidget(font_size_widget)

        menu.addAction(font_box_item)
        menu.addAction(font_size_item)
        menu.exec_(QCursor.pos())

    def content_view_context_menu(self):
        menu = QMenu()
        try:
            content = self.content_model.content_list[self.content_list_view.selectedIndexes()[0].row()]
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

    def set_post_text_font(self, font=None, size=None):
        """
        Sets the font and size of the post text browser.
        :param font: The font that the post text browser should be set to display.
        :param size: The size of the font for the post text browser
        """
        if font is not None:
            self.post_text_font = font
            font.setPointSize(self.post_text_font_size)
            self.post_text_font = font
            self.post_text_browser.setFont(font)
        if size is not None:
            self.post_text_font_size = size
            font = self.post_text_browser.font()
            font.setPointSize(size)
            self.post_text_font = font
            self.post_text_browser.setFont(font)

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
        content = self.content_model.content_list[self.content_list_view.selectedIndexes()[0].row()]
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
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_post(self):
        if self.show_posts:
            try:
                self.current_post = self.post_model.get_item(self.post_table_view.currentIndex().row())
            except IndexError:
                self.current_post = None
            if self.cascade:
                self.setup_call_list.append('POST')
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_current_comment(self):
        if self.show_comments:
            # self.current_comment = \
            #     self.comment_tree_model.get_item()
            if self.cascade:
                self.setup_call_list.append('COMMENT')
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
                self.cascade_setup()
                self.setup_call_list.clear()

    def set_download_session_data(self):
        f = DownloadSessionFilter()
        filter_tups = self.filter.filter(DownloadSession)
        query = self.session.query(DownloadSession)
        if self.reddit_object_focus:
            dl_ids = self.session.query(Post.download_session_id)\
                .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
            query = query.filter(DownloadSession.id.in_(dl_ids))
        elif self.post_focus:
            query = query.filter(DownloadSession.id == self.current_post.download_session_id)
        elif self.content_focus:
            query = query.filter(DownloadSession.id == self.current_content.download_session_id)
        elif self.comment_focus:
            query = query.filter(DownloadSession.id == self.current_comment.download_session_id)
        self.download_session_model.set_data(f.filter(self.session, *filter_tups, query=query,
                                                      order_by=self.download_session_order).all())

    def set_reddit_object_data(self):
        f = RedditObjectFilter()
        filter_tups = self.filter.filter(RedditObject)
        query = self.session.query(RedditObject).filter(RedditObject.significant == True)
        if self.download_session_focus:
            subquery = self.session.query(Post.significant_reddit_object_id)\
                .filter(Post.download_session_id == self.current_download_session.id)
            query = query.filter(RedditObject.id.in_(subquery))
        elif self.post_focus:
            query = query.filter(RedditObject.id == self.current_post.significant_reddit_object_id)
        elif self.content_focus:
            query = query.filter(RedditObject.id == self.current_content.post.significant_reddit_object_id)
        elif self.comment_focus:
            query = query.filter(RedditObject.id == self.current_comment.post.significant_reddit_object_id)
        self.reddit_object_model.set_data(f.filter(self.session, *filter_tups, query=query,
                                                   order_by=self.reddit_object_order).all())

    def set_post_data(self):
        f = PostFilter()
        filter_tups = self.filter.filter(Post)
        query = self.session.query(Post)
        if self.download_session_focus or self.reddit_object_focus:
            if self.show_download_sessions:
                query = query.filter(Post.download_session_id == self.current_download_session.id)
            if self.show_reddit_objects:
                query = query.filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
        elif self.content_focus:
            query = query.filter(Post.id == self.current_content.post_id)
        elif self.comment_focus:
            query = query.filter(Post.id == self.current_comment.post_id)
        self.post_model.set_data(f.filter(self.session, *filter_tups, query=query, order_by=self.post_order).all())

    def set_content_data(self):
        f = ContentFilter()
        filter_tups = self.filter.filter(Content)
        query = self.session.query(Content)
        if self.download_session_focus:
            query = query.filter(Content.download_session_id == self.current_download_session.id)
            if self.show_posts:
                query = query.filter(Content.post_id == self.current_post.id)
            elif self.show_reddit_objects:
                posts = self.session.query(Post.id) \
                    .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
                query = query.fitler(Content.post_id.in_(posts))
        elif self.reddit_object_focus:
            posts = self.session.query(Post.id) \
                .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
            query = query.filter(Content.post_id.in_(posts))
            if self.show_posts:
                query = query.filter(Content.post_id == self.current_post.id)
            elif self.show_download_sessions:
                query = query.filter(Content.download_session_id == self.current_download_session.id)
        elif self.post_focus:
            query = query.filter(Content.post_id == self.current_post.id)
        elif self.comment_focus:
            query = query.filter(Content.comment_id == self.current_comment)
        self.content_model.set_data(f.filter(self.session, *filter_tups, query=query, order_by=self.content_order)
                                    .all())

    def set_comment_data(self):
        f = CommentFilter()
        filter_tups = self.filter.filter(Comment)
        query = self.session.query(Comment)
        if self.download_session_focus:
            if self.show_posts:
                query = query.filter(Comment.post_id == self.current_post.id)
            elif self.show_reddit_objects:
                posts = self.session.query(Post.id)\
                    .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
                query = query.filter(Comment.post_id.in_(posts))
            else:
                query = query.filter(Comment.download_session_id == self.current_download_session.id)
        if self.reddit_object_focus:
            if self.show_posts:
                query = query.filter(Comment.post_id == self.current_post.id)
            elif self.show_reddit_objects:
                posts = self.session.query(Post.id) \
                    .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
                query = query.filter(Comment.post_id.in_(posts))
        elif self.post_focus:
            query = query.filter(Comment.post_id == self.current_post.id)
        elif self.content_focus:
            query = query.filter(Comment.post_id == self.current_content.comment_id)
        self.comment_tree_model.set_data(f.filter(self.session, *filter_tups, query=query, order_by=self.comment_order)\
                                         .all())

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
            first_index = self.comment_tree_model.createIndex(0, 0)
            if self.comment_tree_view.currentIndex() != first_index:
                self.comment_tree_view.setCurrentIndex(first_index)
            else:
                self.set_current_comment()