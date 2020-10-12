import logging

from .runner import Runner, verify_run
from ..core.comment_filter import CommentFilter
from ..core.submittable_creator import SubmittableCreator
from ..utils import injector


class CommentHandler(Runner):

    def __init__(self, submission, post, download_session_id, stop_run, session=None):
        super().__init__(stop_run)
        self.logger = logging.getLogger(__name__)
        self.db = injector.get_database_handler()
        self.submission = submission
        self.post = post
        self.significant_ro = self.post.significant_reddit_object
        self.sort_order = self.get_sort_order()
        self.download_session_id = download_session_id
        self.session = session

        self.comment_filter = CommentFilter()
        self.comments_to_download = []
        self.comments_to_extract_links = []

        self.working_comments = {}
        self.depth = 0

    def get_sort_order(self):
        sort_method = self.significant_ro.comment_sort_method
        if sort_method.value == 6:
            return 'q&a'
        else:
            return sort_method.name.lower()

    def run(self):
        if self.session is not None:
            self.extract_comments(self.session)
        else:
            with self.db.get_scoped_session() as session:
                self.extract_comments(session)

    @verify_run
    def extract_comments(self, session):
        self.submission.comment_sort = self.sort_order
        self.submission.comment_limit = self.significant_ro.comment_limit
        self.submission.comments.replace_more(limit=0)
        for praw_comment in self.submission.comments:
            comment_id = self.handle_found_comment(praw_comment, session)
            if comment_id is not None:
                self.working_comments[praw_comment] = comment_id
        while len(self.working_comments) > 0:
            self.cascade_comments(session)

    @verify_run
    def cascade_comments(self, session):
        self.depth += 1
        if self.depth < self.significant_ro.comment_depth:
            next_level_comments = {}
            for praw_comment, comment_id in self.working_comments.items():
                praw_comment.reply_sort = self.sort_order
                # TODO: try adding replace more here
                praw_comment.replies.replace_more(limit=0)
                for reply in praw_comment.replies[: self.significant_ro.comment_reply_limit]:
                    reply_id = self.handle_found_comment(reply, session, comment_id)
                    if reply_id is not None:
                        next_level_comments[reply] = reply_id
            self.working_comments = next_level_comments
        else:
            self.working_comments.clear()

    @verify_run
    def handle_found_comment(self, praw_comment, session, parent_id=None):
        if self.comment_filter.filter_extraction(praw_comment, self.significant_ro) and \
                self.comment_filter.filter_score_limit(praw_comment, self.significant_ro):
            comment = SubmittableCreator.create_comment(praw_comment, self.post, session, self.download_session_id,
                                                        parent_comment_id=parent_id)
            if comment is not None:
                if self.comment_filter.filter_download(praw_comment, self.significant_ro):
                    self.comments_to_download.append(comment)
                if self.comment_filter.filter_content_download(praw_comment, self.significant_ro):
                    self.comments_to_extract_links.append(comment)
                return comment.id
        return None
