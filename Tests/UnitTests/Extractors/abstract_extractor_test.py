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

    def check_output(self, extractor, url, post):
        content = extractor.extracted_content[0]
        self.assertEqual(url, content.url)
        self.assertEqual(post.title, content.title)
        self.assertEqual(post, content.post)
        self.assertEqual(post.author, content.user)
        self.assertEqual(post.subreddit, content.subreddit)
        self.assertIsNotNone(content.id)
