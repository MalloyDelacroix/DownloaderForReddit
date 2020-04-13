import os

from .SelfPostExtractor import SelfPostExtractor


class CommentExtractor(SelfPostExtractor):

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)

    def extract_content(self):
        try:
            ext = self.settings_manager.comment_file_format  # TODO: move this to reddit object
            title = self.make_title()
            directory = self.make_dir_path()
            self.create_dir_path(directory)
            self.download_text(directory, title, ext)
        except Exception as e:
            self.failed_extraction = True
            self.failed_extraction_message = f'Failed to save comment text. ERROR: {e}'
            self.logger.error('Failed to save content text', extra={
                'url': self.url, 'user': self.comment.url, 'subreddit': self.comment.subreddit,
                'comment_id': self.comment.id, 'comment_reddit_id': self.comment.reddit_id,
                'date_posted': self.comment.date_posted
            })

    def download_text(self, dir_path, title, extension):
        try:
            self.create_dir_path(dir_path)
            path = os.path.join(dir_path, title) + f'.{extension}'
            with open(path, 'w', encoding='utf-8') as file:
                text = self.get_text(extension)
                file.write(text)
        except:
            self.logger.error('Failed to download comment text', extra={'post': self.post.title,
                                                                        'post_id': self.post.id,
                                                                        'comment_id': self.comment.id,
                                                                        'directory_path': dir_path, 'title': title},
                              exc_info=True)
