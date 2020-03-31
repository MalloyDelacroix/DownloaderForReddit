import os
import logging
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QModelIndex

from ..Database.Models import RedditObject, Post, Content, Comment
from ..GUI_Resources.DownloadSessionsDialog_auto import Ui_DownloadSessionDialog
from ..ViewModels.DownloadSessionViewModels import (DownloadSessionModel, RedditObjectModel, PostTableModel,
                                                    ContentListView)
from ..Utils import Injector


class DownloadSessionDialog(QDialog, Ui_DownloadSessionDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = Injector.get_database_handler()
        self.session = self.db.get_session()

        self.show_reddit_objects = True
        self.show_posts = True
        self.show_content = True
        self.show_comments = True

        self.current_download_session = None
        self.current_reddit_object = None
        self.current_post = None

        self.download_session_model = DownloadSessionModel()
        self.download_session_list_view.setModel(self.download_session_model)

        self.reddit_object_model = RedditObjectModel()
        self.reddit_object_list_view.setModel(self.reddit_object_model)

        self.post_model = PostTableModel()
        self.post_table_view.setModel(self.post_model)

        self.content_model = ContentListView()
        self.content_list_view.setModel(self.content_model)

        self.download_session_list_view.clicked.connect(self.set_current_download_session)

    def set_current_download_session(self):
        self.current_download_session = \
            self.download_session_model.sessions[self.download_session_list_view.currentIndex().row()]
        if self.show_reddit_objects:
            self.reddit_object_model.set_data(
                self.current_download_session.get_downloaded_reddit_objects(session=self.session).all())
            self.set_current_reddit_object()

    def set_current_reddit_object(self, new_object=None):
        if new_object is None:
            new_object = self.reddit_object_model.reddit_object_list[0]
        self.current_reddit_object = new_object
        if self.show_posts:
            self.post_model.posts = self.session.query(Post)\
                .filter(Post.download_session_id == self.current_download_session.id)

    def set_current_post(self):
        pass
