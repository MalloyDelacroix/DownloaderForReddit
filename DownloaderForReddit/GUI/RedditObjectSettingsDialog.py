import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread

from ..GUI_Resources.RedditObjectSettingsDialog_auto import Ui_RedditObjectSettingsDialog
from ..ViewModels.RedditObjectListModel import RedditObjectListModel
from ..Database.Models import RedditObject, Post, Content, Comment
from ..Utils import Injector


class RedditObjectSettingsDialog(QtWidgets.QDialog, Ui_RedditObjectSettingsDialog):

    def __init__(self, list_type, list_name, selected_object: RedditObject):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.db = Injector.get_database_handler()
        self.list_type = list_type
        self.list_name = list_name
        self.r = selected_object

        self.list_model = RedditObjectListModel(self.list_type)
        self.list_model.set_list(self.list_name)
        self.reddit_objects_list_view.setModel(self.list_model)
        self.setup_display()

    def setup_display(self):
        self.set_basic_info()
        self.set_download_info()

    def set_basic_info(self):
        self.name_label.setText(self.r.name)
        self.id_label.setText(str(self.r.id))
        self.date_created_label.setText(self.r.date_created_display)
        self.date_added_label.setText(self.r.date_added_display)
        self.last_download_label.setText(self.r.last_download_display)

    def set_download_info(self):
        self.download_info_thread = Thread(target=self.set_download_info_labels)
        self.download_info_thread.start()

    def set_download_info_labels(self):
        with self.db.get_scoped_session() as session:
            post_count = session.query(Post.id).filter(Post.significant_reddit_object_id == self.r.id).count()
            comment_count = session.query(Comment.id).filter(Comment.significant_reddit_object_id == self.r.id).count()
            content_count = session.query(Content.id).filter(Content.post_id.in_(
                session.query(Post.id).filter(Post.significant_reddit_object_id == self.r.id))
            )
            self.post_count_label.setText(post_count)
            self.comment_count_label.setText(comment_count)
            self.content_count_label.setText(content_count)
