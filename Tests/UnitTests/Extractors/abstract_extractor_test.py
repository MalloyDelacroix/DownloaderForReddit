from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.database.database_handler import DatabaseHandler
from DownloaderForReddit.utils import injector


class ExtractorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = MagicMock()
        injector.settings_manager = cls.settings

    def setUp(self):
        self.db = DatabaseHandler(in_memory=True)
        self.session = self.db.get_session()

    def tearDown(self):
        self.session.close()

    def check_output_multiple(self, extractor, url_list, post):
        count = 1
        for content, url in zip(extractor.extracted_content, url_list):
            title = f'{post.title} {count}'
            self.check(content, url, post, title=title)
            count += 1

    def check_output(self, extractor, url, post, **kwargs):
        content = extractor.extracted_content[0]
        self.check(content, url, post, **kwargs)

    def check(self, content, url, post, **kwargs):
        self.assertEqual(url, content.url)
        self.assertEqual(kwargs.get('title', post.title), content.title)
        self.assertEqual(post, content.post)
        self.assertEqual(post.author, content.user)
        self.assertEqual(post.subreddit, content.subreddit)
        self.assertIsNotNone(content.id)
