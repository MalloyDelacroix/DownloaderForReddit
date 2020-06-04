from threading import Thread
from PyQt5.QtWidgets import QWidget

from ...guiresources.widgets.object_info_widget_auto import Ui_ObjectInfoWidget
from ...database.models import Post, Comment, Content, RedditObject, RedditObjectList, ListAssociation, User, Subreddit
from ...utils import injector


class ObjectInfoWidget(QWidget, Ui_ObjectInfoWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.db = injector.get_database_handler()
        self.object_type = None
        self.selected_objects = []

    @property
    def single_object(self):
        return len(self.selected_objects) == 1

    def set_objects(self, object_list):
        if object_list:
            self.selected_objects = object_list
            self.object_type = object_list[0].object_type
            self.set_basic_info()
            self.set_download_info()

    def set_basic_info(self):
        if self.single_object:
            selected_object = self.selected_objects[0]
            self.name_label.setText(selected_object.name)
            self.id_label.setText(str(selected_object.id))
            self.date_created_label.setText(selected_object.date_created_display)
            self.date_added_label.setText(selected_object.date_added_display)
            self.last_download_label.setText(selected_object.last_download_display)
        else:
            for label in [self.name_label, self.id_label, self.date_created_label, self.date_added_label,
                          self.last_download_label]:
                label.setText('')

    def set_download_info(self):
        self.download_info_thread = Thread(target=self.set_download_info_labels)
        self.download_info_thread.start()

    def set_download_info_labels(self):
        with self.db.get_scoped_session() as session:
            if self.object_type == 'REDDIT_OBJECT_LIST':
                id_list = session.query(ListAssociation.reddit_object_id)\
                    .filter(RedditObjectList.id.in_([x.id for x in self.selected_objects]))
            else:
                id_list = [x.id for x in self.selected_objects]
            post_count = session.query(Post.id).filter(Post.significant_reddit_object_id.in_(id_list)).count()
            content_count = session.query(Content.id) \
                .filter(Content.post_id.in_(session.query(Post.id)
                                            .filter(Post.significant_reddit_object_id.in_(id_list)))).count()
            associated_comment_count = session.query(Comment.id).join(Post) \
                .filter(Post.significant_reddit_object_id.in_(id_list)).count()

            self.post_count_label.setText(str(post_count))
            self.content_count_label.setText(str(content_count))
            self.associated_comment_count_label.setText(str(associated_comment_count))

            user = self.object_type == 'USER'
            self.comment_author_label.setVisible(user)
            self.comment_author_count_label.setVisible(user)
            if user:
                comment_author_count = session.query(Comment.id).filter(Comment.author_id.in_(id_list)).count()
                self.comment_author_count_label.setText(str(comment_author_count))
