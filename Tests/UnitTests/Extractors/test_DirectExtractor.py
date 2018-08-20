import unittest
import logging

from DownloaderForReddit.Extractors.DirectExtractor import DirectExtractor
from DownloaderForReddit.Utils import Injector
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


class TestDirectExtractor(unittest.TestCase):

    logging.disable(logging.CRITICAL)

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()

    def test_extract_direct_link(self):
        link = 'https://unsupported_site.com/image/3jfd9nlksd.jpg'
        post = MockObjects.get_generic_mock_post()
        post.url = link
        de = DirectExtractor(post, MockObjects.get_blank_user())
        de.extract_content()

        content = de.extracted_content[0]
        self.assertEqual(link, content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/3jfd9nlksd.jpg', content.filename)
