import os

from .base_extractor import BaseExtractor
from ..database import Content
from ..utils import system_util


class SelfPostExtractor(BaseExtractor):

    url_key = None

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)
        self.download_session_id = kwargs.get('download_session_id', None)

    def extract_content(self):
        try:
            ext = self.significant_reddit_object.self_post_file_format
            directory = self.make_dir_path()
            if self.content_filter.filter_duplicate(self.post, self.url):
                self.create_dir_path(directory)
                self.make_content(self.url, ext)
        except Exception as e:
            self.failed_extraction = True
            self.failed_extraction_message = f'Failed to save self post.  ERROR: {e}'
            self.logger.error('Failed to save self post',
                              extra={'url': self.url, 'user': self.user, 'subreddit': self.subreddit}, exc_info=True)

    def make_content(self, url, extension, count=None, name_modifier=None):
        content = Content(
            title=self.make_title(),
            extension=extension,
            url=url,
            user=self.user,
            subreddit=self.subreddit,
            post=self.post,
            directory_path=self.make_dir_path()
        )
        self.check_file_path(content)
        self.download_text_post(content)
        session = self.post.get_session()
        session.add(content)
        session.commit()
        return content

    def download_text_post(self, content):
        try:
            with open(content.get_full_file_path(), 'w', encoding='utf-8') as file:
                text = self.get_text(content.extension)
                file.write(text)
                content.set_downloaded(self.download_session_id)
        except Exception as e:
            content.set_download_error('Failed to save text post', extra={'error': e})

    def get_text(self, ext):
        if ext == 'txt':
            return self.comment.body if self.comment is not None else self.post.text
        else:
            return self.comment.body_html if self.comment is not None else self.post.text_html

    def check_file_path(self, content):
        self.create_dir_path(content.directory_path)
        unique_count = 1
        base_path = system_util.clean_path(content.title)
        download_title = base_path
        path = content.get_full_file_path(download_title)
        while os.path.exists(path):
            download_title = f'{base_path}({unique_count})'
            path = content.get_full_file_path(download_title)
            unique_count += 1
        content.download_title = download_title

    def create_dir_path(self, dir_path):
        try:
            system_util.create_directory(dir_path)
        except PermissionError:
            self.logger.error('Could not create directory path', extra={'directory_path': dir_path}, exc_info=True)
