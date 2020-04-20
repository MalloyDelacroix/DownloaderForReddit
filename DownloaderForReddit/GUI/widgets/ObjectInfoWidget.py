from threading import Thread
from PyQt5.QtWidgets import QWidget

from ...GUI_Resources.widgets.ObjectInfoWidget_auto import Ui_ObjectInfoWidget
from ...Database.Models import Post, Comment, Content, RedditObject, RedditObjectList, ListAssociation, User, Subreddit
from ...Utils import Injector


class ObjectInfoWidget(QWidget, Ui_ObjectInfoWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.db = Injector.get_database_handler()

    def set_object(self, obj):
        if obj:
            self.selected_object = obj
            self.set_basic_info()
            self.set_download_info()

    def set_basic_info(self):
        self.name_label.setText(self.selected_object.name)
        self.id_label.setText(str(self.selected_object.id))
        self.date_created_label.setText(self.selected_object.date_created_display)
        self.date_added_label.setText(self.selected_object.date_added_display)
        self.last_download_label.setText(self.selected_object.last_download_display)

    def set_download_info(self):
        self.download_info_thread = Thread(target=self.set_download_info_labels)
        self.download_info_thread.start()

    def set_download_info_labels(self):
        if type(self.selected_object) == RedditObject or type(self.selected_object) == User or \
                type(self.selected_object) == Subreddit:
            self.set_download_info_labels_for_reddit_object(type(self.selected_object) == User)
        elif type(self.selected_object) == RedditObjectList:
            self.set_download_info_labels_for_object_list(self.selected_object.list_type == 'USER')

    def set_download_info_labels_for_reddit_object(self, user=False):
        with self.db.get_scoped_session() as session:
            post_count = session.query(Post.id) \
                .filter(Post.significant_reddit_object_id == self.selected_object.id).count()
            content_count = session.query(Content.id) \
                .filter(Content.post_id.in_(session.query(Post.id).filter(
                Post.significant_reddit_object_id == self.selected_object.id))).count()
            associated_comment_count = session.query(Comment.id).join(Post) \
                .filter(Post.significant_reddit_object_id == self.selected_object.id).count()
            self.post_count_label.setText(str(post_count))
            self.content_count_label.setText(str(content_count))
            self.associated_comment_count_label.setText(str(associated_comment_count))
            self.comment_author_label.setVisible(user)
            self.comment_author_count_label.setVisible(user)
            if user:
                comment_author_count = session.query(Comment.id) \
                    .filter(Comment.author_id == self.selected_object.id).count()
                self.comment_author_count_label.setText(str(comment_author_count))

    def set_download_info_labels_for_object_list(self, user=False):
        with self.db.get_scoped_session() as session:
            list_object_ids = session.query(ListAssociation.reddit_object_id)\
                .filter(RedditObjectList.id == self.selected_object.id)
            post_count = session.query(Post.id) \
                .filter(Post.significant_reddit_object_id.in_(list_object_ids)).count()
            content_count = session.query(Content.id) \
                .filter(Content.post_id.in_(session.query(Post.id)
                                            .filter(Post.significant_reddit_object_id.in_(list_object_ids)))).count()
            associated_comment_count = session.query(Comment.id).join(Post) \
                .filter(Post.significant_reddit_object_id.in_(list_object_ids)).count()
            self.post_count_label.setText(str(post_count))
            self.content_count_label.setText(str(content_count))
            self.associated_comment_count_label.setText(str(associated_comment_count))
            self.comment_author_label.setVisible(user)
            self.comment_author_count_label.setVisible(user)
            if user:
                comment_author_count = session.query(Comment.id) \
                    .filter(Comment.author_id.in_(list_object_ids)).count()
                self.comment_author_count_label.setText(str(comment_author_count))
