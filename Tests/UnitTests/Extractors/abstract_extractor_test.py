from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.database.database_handler import DatabaseHandler
from DownloaderForReddit.utils import injector


class ExtractorTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseHandler(in_memory=True)
        cls.settings = MagicMock()
        injector.settings_manager = cls.settings

    def setUp(self):
        self.session = self.db.get_session()

    def tearDown(self):
        self.session.close()
