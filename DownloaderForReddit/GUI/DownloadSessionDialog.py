import logging
from PyQt5.QtWidgets import (QDialog, QMenu, QWidgetAction, QInputDialog, QSpinBox, QLabel, QHBoxLayout, QWidget,
                             QActionGroup)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor

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

        self.reddit_object_list_view.setVisible(self.show_reddit_objects_checkbox.isChecked())
        self.post_table_view.setVisible(self.show_posts_checkbox.isChecked())
        self.content_list_view.setVisible(self.show_content_checkbox.isChecked())
        self.comment_tree_view.setVisible(self.show_comments_checkbox.isChecked())

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

    def content_view_context_menu(self):
        menu = QMenu()
        icon_menu = QMenu('Icon Size')
        action_group = QActionGroup(self)
        extra_small_item = self.add_icon_menu_item(icon_menu, action_group, 'Extra Small', 72)
        small_item = self.add_icon_menu_item(icon_menu, action_group, 'Small', 110)
        medium_item = self.add_icon_menu_item(icon_menu, action_group, 'Medium', 76)
        large_item = self.add_icon_menu_item(icon_menu, action_group, 'Large', 256)
        extra_large_item = self.add_icon_menu_item(icon_menu, action_group, 'Extra Large', 420)

        custom_item = CustomIconSizeMenuItem(self.icon_size, parent=self)
        custom_item.triggered.connect(lambda: self.set_content_icon_size(custom_item.spin_box.value()))
        custom_item.triggered.connect(menu.close)
        custom_item.setChecked(not any(x.isChecked() for x in icon_menu.actions()))
        icon_menu.addAction(custom_item)
        action_group.addAction(custom_item)

        menu.addMenu(icon_menu)
        menu.exec_(QCursor.pos())

    def add_icon_menu_item(self, icon_menu, action_group, text, icon_size):
        item = icon_menu.addAction(text, lambda: self.set_content_icon_size(icon_size))
        item.setCheckable(True)
        item.setChecked(icon_size == self.icon_size)
        action_group.addAction(item)
        return item

    def toggle_reddit_object_view(self):
        if self.show_reddit_objects_checkbox.isChecked():
            self.reddit_object_list_view.setVisible(True)
            self.set_reddit_object_model_data()
            self.set_first_reddit_object_index()
        else:
            self.reddit_object_list_view.setVisible(False)
            if self.show_posts_checkbox.isChecked():
                self.set_post_model_data()
                self.set_first_post_index()
            else:
                self.set_content_model_data()

    def toggle_post_view(self):
        if self.show_posts_checkbox.isChecked():
            self.post_table_view.setVisible(True)
            self.set_post_model_data()
            self.set_first_post_index()
        else:
            self.post_table_view.setVisible(False)
            self.set_content_model_data()

    def toggle_content_view(self):
        self.set_content_model_data()
        self.content_list_view.setVisible(self.show_content_checkbox.isChecked())

    def toggle_comment_view(self):
        self.set_comment_model_data()
        self.comment_tree_view.setVisible(self.show_comments_checkbox.isChecked())

    def set_content_icon_size(self, size=None):
        if size is None:
            size = self.icon_size
        else:
            self.icon_size = size
        self.content_list_view.setIconSize(QSize(size, size))
        self.content_list_view.setGridSize(QSize(size + 2, size + 50))

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


class CustomIconSizeMenuItem(QWidgetAction):

    def __init__(self, current_icon_size, parent=None):
        super().__init__(parent)

        widget = QWidget(None)
        layout = QHBoxLayout()
        self.label = QLabel('Custom')
        self.spin_box = QSpinBox()
        self.spin_box.setValue(current_icon_size)
        self.spin_box.setMinimum(20)
        self.spin_box.setMaximum(800)
        self.spin_box.setSingleStep(10)
        self.spin_box.keyPressEvent = self.handle_event
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)

        widget.setLayout(layout)
        self.setDefaultWidget(widget)

        self.setCheckable(True)

    def handle_event(self, event):
        key = event.key()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            self.trigger()
        else:
            super(QSpinBox, self.spin_box).keyPressEvent(event)
