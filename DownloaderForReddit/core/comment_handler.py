from typing import Optional
from praw.models import Comment as PrawComment
from sqlalchemy.orm.session import Session

from .runner import Runner, verify_run
from ..database.models import Post
from ..core.comment_filter import CommentFilter
from ..core.submittable_creator import SubmittableCreator
from ..utils import injector


class CommentHandler(Runner):

    def __init__(self, submission, post, download_session_id, stop_run, session=None):
        super().__init__(stop_run)
        self.db = injector.get_database_handler()
        self.submission = submission
        self.post = post
        self.download_session_id = download_session_id
        self.session = session

        self.comment_filter = CommentFilter()
        self.comments_to_download = []
        self.comments_to_extract_links = []

    def run(self):
        if self.session is not None:
            self.extract_comments(self.session)
        else:
            with self.db.get_scoped_session() as session:
                self.extract_comments(session)

    @verify_run
    def extract_comments(self, session):
        significant_ro = self.post.significant_reddit_object
        sort_method = significant_ro.comment_sort_method
        if sort_method.value == 6:
            sort_method = 'q&a'
        else:
            sort_method = sort_method.name.lower()
        self.submission.comment_sort = sort_method
        self.submission.comments.replace_more(limit=0)
        for praw_comment in self.submission.comments[: significant_ro.comment_limit]:
            self.cascade_comments(praw_comment, self.post, session)

    @verify_run
    def cascade_comments(self, praw_comment: PrawComment, post: Post, session: Session,
                         parent_id: Optional[int] = None):
        significant_ro = post.significant_reddit_object
        if self.comment_filter.filter_extraction(praw_comment, significant_ro) and \
                self.comment_filter.filter_score_limit(praw_comment, significant_ro):
            comment = SubmittableCreator.create_comment(praw_comment, post, session, self.download_session_id,
                                                        parent_comment_id=parent_id)
            if comment is not None:
                if self.comment_filter.filter_download(comment, post.significant_reddit_object):
                    self.comments_to_download.append(comment)
                if self.comment_filter.filter_content_download(comment, post.significant_reddit_object):
                    self.comments_to_extract_links.append(comment)

                praw_comment.replies.replace_more(limit=0)
                for sub_comment in praw_comment.replies:
                    self.cascade_comments(sub_comment, post, session, parent_id=comment.id)
