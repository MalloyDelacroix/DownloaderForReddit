from .SelfPostExtractor import SelfPostExtractor


class CommentExtractor(SelfPostExtractor):

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)

    def extract_content(self):
        try:
            ext = self.settings_manager.comment_file_format
            directory = self.make_dir_path()
            self.create_dir_path(directory)
            self.make_content(self.comment.url, ext)
        except Exception as e:
            self.failed_extraction = True
            self.failed_extraction_message = f'Failed to save comment text. ERROR: {e}'
            self.logger.error('Failed to save content text', extra={
                'url': self.url, 'user': self.comment.url, 'subreddit': self.comment.subreddit,
                'comment_id': self.comment.id, 'comment_reddit_id': self.comment.reddit_id,
                'date_posted': self.comment.date_posted
            })
