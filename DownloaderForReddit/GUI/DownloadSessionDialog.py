import logging
from PyQt5.QtWidgets import (QDialog, QMenu, QWidgetAction, QInputDialog, QFontComboBox, QComboBox, QActionGroup,
                             QWidget, QHBoxLayout, QLabel)
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QCursor, QFont

from ..Database.Models import DownloadSession, RedditObject, Post, Content, Comment
from ..GUI_Resources.DownloadSessionsDialog_auto import Ui_DownloadSessionDialog
from ..ViewModels.DownloadSessionViewModels import (DownloadSessionModel, RedditObjectModel, PostTableModel,
                                                    ContentListView)
from ..Utils import Injector, SystemUtil


class DownloadSessionDialog(QDialog, Ui_DownloadSessionDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()

        geom = self.settings_manager.dls_dialog_geom
        self.resize(geom['width'], geom['height'])
        if geom['x'] != 0 and geom['y'] != 0:
            self.move(geom['x'], geom['y'])
        self.splitter.setSizes(self.settings_manager.dls_dialog_splitter_position)

        self.show_reddit_objects_checkbox.setChecked(self.settings_manager.dls_dialog_show_reddit_objects)
        self.show_posts_checkbox.setChecked(self.settings_manager.dls_dialog_show_posts)
        self.show_content_checkbox.setChecked(self.settings_manager.dls_dialog_show_content)
        self.show_comments_checkbox.setChecked(self.settings_manager.dls_dialog_show_comments)

        self.post_text_font_size = self.settings_manager.dls_dialog_post_text_font_size
        self.post_text_font = QFont(self.settings_manager.dls_dialog_post_text_font, self.post_text_font_size)
        self.icon_size = self.settings_manager.dls_dialog_icon_size

        self.current_download_session = None
        self.current_reddit_object = None
        self.current_post = None

        self.download_session_model = DownloadSessionModel()
        self.download_session_model.sessions = \
            self.session.query(DownloadSession).order_by(DownloadSession.start_time.desc()).all()
        self.download_session_list_view.setModel(self.download_session_model)

        self.reddit_object_model = RedditObjectModel()
        self.reddit_object_list_view.setModel(self.reddit_object_model)

        self.post_model = PostTableModel()
        self.post_table_view.setModel(self.post_model)

        self.set_content_icon_size()
        self.content_model = ContentListView()
        self.content_list_view.setModel(self.content_model)

        self.reddit_object_widget.setVisible(self.show_reddit_objects_checkbox.isChecked())
        self.post_widget.setVisible(self.show_posts_checkbox.isChecked())
        self.content_widget.setVisible(self.show_content_checkbox.isChecked())
        self.comment_widget.setVisible(self.show_comments_checkbox.isChecked())

        self.post_text_browser.setVisible(False)
        font = QFont(self.settings_manager.dls_dialog_post_text_font,
                     self.settings_manager.dls_dialog_post_text_font_size)
        self.post_text_browser.setFont(font)

        self.show_reddit_objects_checkbox.stateChanged.connect(self.toggle_reddit_object_view)
        self.show_posts_checkbox.stateChanged.connect(self.toggle_post_view)
        self.show_content_checkbox.stateChanged.connect(self.toggle_content_view)
        self.show_comments_checkbox.stateChanged.connect(self.toggle_comment_view)

        self.download_session_list_view.selectionModel().selectionChanged.connect(self.set_current_download_session)
        self.reddit_object_list_view.selectionModel().selectionChanged.connect(self.set_current_reddit_object)
        self.post_table_view.selectionModel().selectionChanged.connect(self.set_current_post)
        self.content_list_view.doubleClicked.connect(self.open_selected_content)

        self.download_session_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.download_session_list_view.customContextMenuRequested.connect(self.download_session_view_context_menu)

        headers = self.post_table_view.horizontalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self.post_headers_context_menu)
        headers.setSectionsMovable(True)
        for key, value in self.settings_manager.dls_post_table_headers.items():
            index = self.post_model.headers.index(key)
            headers.setSectionHidden(index, value)

        self.post_text_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.post_text_browser.customContextMenuRequested.connect(self.post_text_browser_context_menu)

        self.content_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_list_view.customContextMenuRequested.connect(self.content_view_context_menu)

        self.set_first_session_index()

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
        pass

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

    def toggle_reddit_object_view(self):
        if self.show_reddit_objects_checkbox.isChecked():
            self.reddit_object_widget.setVisible(True)
            self.set_reddit_object_model_data()
            self.set_first_reddit_object_index()
        else:
            self.reddit_object_widget.setVisible(False)
            if self.show_posts_checkbox.isChecked():
                self.set_post_model_data()
                self.set_first_post_index()
            else:
                self.set_content_model_data()

    def toggle_post_view(self):
        if self.show_posts_checkbox.isChecked():
            self.post_widget.setVisible(True)
            self.set_post_model_data()
            self.set_first_post_index()
        else:
            self.post_widget.setVisible(False)
            self.set_content_model_data()

    def toggle_content_view(self):
        self.set_content_model_data()
        self.content_widget.setVisible(self.show_content_checkbox.isChecked())

    def toggle_comment_view(self):
        self.set_comment_model_data()
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

    def set_current_download_session(self):
        try:
            self.current_download_session = \
                self.download_session_model.sessions[self.download_session_list_view.currentIndex().row()]
        except IndexError:
            pass
        if self.show_reddit_objects_checkbox.isChecked():
            self.set_reddit_object_model_data()
            self.set_first_reddit_object_index()
        elif self.show_posts_checkbox.isChecked():
            self.set_post_model_data()
            self.set_first_post_index()
        else:
            self.set_content_model_data()
            self.set_comment_model_data()

    def set_current_reddit_object(self):
        if self.show_reddit_objects_checkbox.isChecked():
            try:
                self.current_reddit_object = \
                    self.reddit_object_model.reddit_object_list[self.reddit_object_list_view.currentIndex().row()]
            except IndexError:
                pass
            if self.show_posts_checkbox.isChecked():
                self.set_post_model_data()
                self.set_first_post_index()
            else:
                self.set_content_model_data()
                self.set_comment_model_data()

    def set_current_post(self):
        if self.show_posts_checkbox.isChecked():
            try:
                self.current_post = self.post_model.posts[self.post_table_view.currentIndex().row()]
                if self.current_post.text is not None and self.current_post.text != '':
                    self.post_text_browser.setVisible(True)
                    self.post_text_browser.setHtml(self.current_post.text_html)
                else:
                    self.post_text_browser.clear()
                    self.post_text_browser.setVisible(False)
            except IndexError:
                pass
            self.set_content_model_data()
            self.set_comment_model_data()

    def set_reddit_object_model_data(self):
        try:
            if self.show_reddit_objects_checkbox.isChecked():
                self.reddit_object_model.set_data(
                    self.current_download_session
                        .get_downloaded_reddit_objects(session=self.session).order_by(RedditObject.name).all())
        except AttributeError:
            pass

    def set_post_model_data(self):
        try:
            if self.show_posts_checkbox.isChecked():
                if self.show_reddit_objects_checkbox.isChecked():
                    data = self.session.query(Post) \
                        .filter(Post.download_session_id == self.current_download_session.id) \
                        .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
                else:
                    data = self.session.query(Post) \
                        .filter(Post.download_session_id == self.current_download_session.id)
                self.post_model.set_data(data.order_by(Post.title).all())
        except AttributeError:
            pass

    def set_content_model_data(self):
        try:
            if self.show_content_checkbox.isChecked():
                self.content_list_view.clearSelection()
                if self.show_posts_checkbox.isChecked():
                    data = self.session.query(Content) \
                        .filter(Content.download_session_id == self.current_download_session.id) \
                        .filter(Content.post_id == self.current_post.id)
                elif self.show_reddit_objects_checkbox.isChecked():
                    data = self.session.query(Content).join(Post) \
                        .filter(Content.download_session_id == self.current_download_session.id) \
                        .filter(Post.significant_reddit_object_id == self.current_reddit_object.id)
                else:
                    data = self.session.query(Content) \
                        .filter(Content.download_session_id == self.current_download_session.id)
                self.content_model.set_data(data.order_by(Content.title).all())
        except AttributeError:
            pass

    def set_comment_model_data(self):
        pass

    def closeEvent(self, event):
        self.settings_manager.dls_dialog_show_reddit_objects = self.show_reddit_objects_checkbox.isChecked()
        self.settings_manager.dls_dialog_show_posts = self.show_posts_checkbox.isChecked()
        self.settings_manager.dls_dialog_show_content = self.show_content_checkbox.isChecked()
        self.settings_manager.dls_dialog_show_comments = self.show_comments_checkbox.isChecked()
        self.settings_manager.dls_dialog_post_text_font = self.post_text_font.family()
        self.settings_manager.dls_dialog_post_text_font_size = self.post_text_font_size
        self.settings_manager.dls_dialog_icon_size = self.icon_size
        self.settings_manager.dls_dialog_geom['width'] = self.width()
        self.settings_manager.dls_dialog_geom['height'] = self.height()
        self.settings_manager.dls_dialog_geom['x'] = self.x()
        self.settings_manager.dls_dialog_geom['y'] = self.y()
        self.settings_manager.dls_dialog_splitter_position = self.splitter.sizes()
        super().closeEvent(event)

    def set_first_session_index(self):
        first_index = self.download_session_model.createIndex(0, 0)
        if self.download_session_list_view.currentIndex() != first_index:
            self.download_session_list_view.setCurrentIndex(first_index)
        else:
            self.set_current_download_session()

    def set_first_reddit_object_index(self):
        first_index = self.reddit_object_model.createIndex(0, 0)
        if self.reddit_object_list_view.currentIndex() != first_index:
            self.reddit_object_list_view.setCurrentIndex(first_index)
        else:
            self.set_current_reddit_object()

    def set_first_post_index(self):
        first_index = self.post_model.createIndex(0, 0)
        if self.post_table_view.currentIndex() != first_index:
            self.post_table_view.setCurrentIndex(first_index)
        else:
            self.set_current_post()

    def open_selected_content(self):
        content = self.content_model.content_list[self.content_list_view.selectedIndexes()[0].row()]
        SystemUtil.open_in_system(content.full_file_path)

    def rename_download_session(self, dl_session):
        if dl_session is not None:
            new_name, ok = QInputDialog.getText(self, 'New Session Name', 'Enter new session name:')
            if ok:
                dl_session.name = new_name
                self.session.commit()
                self.download_session_model.refresh()
