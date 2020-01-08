import unittest
from os import path
from unittest.mock import patch

from bs4 import BeautifulSoup

from DownloaderForReddit.Extractors.VidbleExtractor import VidbleExtractor
from DownloaderForReddit.Utils import Injector
from Tests.MockObjects import MockObjects
from Tests.MockObjects.MockSettingsManager import MockSettingsManager


class TestVidbleExtractor(unittest.TestCase):

    extracted_single_url_show = 'https://vidble.com/toqeUzXBIl_med.jpg'
    extracted_single_url_explore = 'https://vidble.com/toqeUzXBIl.jpg'

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_imgs')
    def test_extract_single_show(self, s_mock):
        s_mock.return_value = self.get_single_soup_show()
        ve = VidbleExtractor(MockObjects.get_mock_post_vidble(), MockObjects.get_blank_user())
        ve.extract_single()

        content = ve.extracted_content[0]
        self.assertEqual(self.extracted_single_url_show, content.url)
        self.check_output(content)
        self.assertTrue(len(ve.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_imgs')
    def test_extract_single_explore(self, s_mock):
        s_mock.return_value = self.get_single_soup_explore()
        post = MockObjects.get_mock_post_vidble()
        post.url = post.url.replace('show', 'explore')
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_single()

        content = ve.extracted_content[0]
        self.assertEqual(self.extracted_single_url_explore, content.url)
        self.check_output(content)
        self.assertTrue(len(ve.failed_extract_posts) == 0)

    def test_extract_album(self):
        pass  # TODO: Find album to make test html page from

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_single')
    def test_extract_content_assignment_single_show(self, es_mock):
        ve = VidbleExtractor(MockObjects.get_mock_post_vidble(), MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_single')
    def test_extract_content_assignment_single_explore(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = post.url.replace('show', 'explore')
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    def test_extract_content_assignment_album(self):
        pass  # TODO: Test this method after an album html file is made

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_direct_link')
    def test_extract_content_assignment_direct(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = self.extracted_single_url_explore
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    def check_output(self, content):
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/toqeUzXBIl.jpg', content.filename)

    def get_single_soup_show(self):
        current_file_path = path.dirname(path.abspath(__file__))
        current_file_path = path.join(current_file_path,'Resources/vidble_single_test_show.html')
        with open(current_file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')

    def get_single_soup_explore(self):
        current_file_path = path.dirname(path.abspath(__file__))
        current_file_path = path.join(current_file_path, 'Resources/vidble_single_test_explore.html')
        with open(current_file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')

    def get_album_soup(self):
        pass
