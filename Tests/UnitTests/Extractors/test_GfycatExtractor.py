import unittest
from unittest.mock import patch
import logging

from DownloaderForReddit.Extractors.GfycatExtractor import GfycatExtractor
from DownloaderForReddit.Utils import Injector
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


class TestGfycatExtractor(unittest.TestCase):

    logging.disable(logging.CRITICAL)

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()

    @patch('DownloaderForReddit.Extractors.GfycatExtractor.get_json')
    def test_extract_single(self, j_mock):
        dir_url = 'https://giant.gfycat.com/KindlyElderlyCony.webm'
        j_mock.return_value = {'gfyItem': {'webmUrl': dir_url}}
        ge = GfycatExtractor(MockObjects.get_mock_post_gfycat(), MockObjects.get_blank_user())
        ge.extract_single()
        j_mock.assert_called_with('https://gfycat.com/cajax/get/KindlyElderlyCony')
        self.check_output(ge, dir_url)

    def test_direct_extraction(self):
        post = MockObjects.get_mock_post_gfycat()
        post.url = post.url + '.webm'
        ge = GfycatExtractor(post, MockObjects.get_blank_user())
        ge.extract_direct_link()
        self.check_output(ge, post.url)

    @patch('DownloaderForReddit.Extractors.GfycatExtractor.extract_single')
    def test_extract_content_assignment_single(self, es_mock):
        ge = GfycatExtractor(MockObjects.get_mock_post_gfycat(), MockObjects.get_blank_user())
        ge.extract_content()

        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.GfycatExtractor.extract_direct_link')
    def test_extract_content_assignment_direct(self, es_mock):
        post = MockObjects.get_mock_post_gfycat()
        post.url += '.webm'
        ge = GfycatExtractor(post, MockObjects.get_blank_user())
        ge.extract_content()

        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.GfycatExtractor.extract_single')
    def test_failed_connection(self, es_mock):
        es_mock.side_effect = ConnectionError()
        ge = GfycatExtractor(MockObjects.get_mock_post_gfycat(), MockObjects.get_blank_user())
        ge.extract_content()
        failed_post = ge.failed_extract_posts[0]
        self.assertTrue('Failed to locate content' in failed_post.status)

    def check_output(self, ge, url):
        content = ge.extracted_content[0]
        self.assertEqual(url, content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/KindlyElderlyCony.webm', content.filename)
        self.assertTrue(len(ge.failed_extract_posts) == 0)
