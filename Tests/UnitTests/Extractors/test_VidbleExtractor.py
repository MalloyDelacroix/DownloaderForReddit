import unittest
from os import path
from unittest.mock import patch

from bs4 import BeautifulSoup

from DownloaderForReddit.extractors.vidble_extractor import VidbleExtractor
from DownloaderForReddit.utils import injector
from Tests.MockObjects import MockObjects
from Tests.MockObjects.MockSettingsManager import MockSettingsManager


class TestVidbleExtractor(unittest.TestCase):

    def setUp(self):
        injector.settings_manager = MockSettingsManager()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_imgs')
    def test_extract_single_show(self, s_mock):
        s_mock.return_value = self.get_single_soup()
        post = MockObjects.get_mock_post_vidble()
        post.url = 'https://vidble.com/show/XOwqxH6Xz9'
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_single()

        content = ve.extracted_content[0]
        self.check_output(content)
        self.assertTrue(len(ve.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_imgs')
    def test_extract_single_explore(self, s_mock):
        s_mock.return_value = self.get_single_soup()
        post = MockObjects.get_mock_post_vidble()
        post.url = 'https://vidble.com/explore/XOwqxH6Xz9'
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_single()

        content = ve.extracted_content[0]
        self.check_output(content)
        self.assertTrue(len(ve.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_json')
    def test_extract_album(self, j_mock):
        post = MockObjects.get_mock_post_vidible_album()
        j_mock.return_value = {"pics":
                                   ["//www.vidble.com/lkPvqs0yh5_med.png",
                                    "//www.vidble.com/F5DgE2O64b.gif",
                                    "//www.vidble.com/XOwqxH6Xz9_med.jpg",
                                    "//www.vidble.com/3a4xNLuO9M_med.png"]}
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_album()

        contents = ve.extracted_content
        self.check_output_album(contents)
        self.assertTrue(len(ve.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_single')
    def test_extract_content_assignment_single_show(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = 'https://vidble.com/show/XOwqxH6Xz9'
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_single')
    def test_extract_content_assignment_single_explore(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = 'https://vidble.com/explore/XOwqxH6Xz9'
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_direct_link')
    def test_extract_content_explore_direct(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = 'https://vidble.com/explore/XOwqxH6Xz9.jpg'
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        self.assertEqual('https://vidble.com/XOwqxH6Xz9.jpg', ve.url)
        es_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_direct_link')
    def test_extract_content_assignment_direct(self, es_mock):
        post = MockObjects.get_mock_post_vidble_direct()
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    def check_output_album(self, contents):
        filenames = ["lkPvqs0yh5.png",
                     "F5DgE2O64b.gif",
                     "XOwqxH6Xz9.jpg",
                     "3a4xNLuO9M.png"
                     ]
        for content, file in zip(contents, filenames):
            self.assertEqual('Picture(s)', content.post_title)
            self.assertEqual('Pics', content.subreddit)
            self.assertEqual(1521473630, content.date_created)
            expected_filename = 'C:/Users/Gorgoth/Downloads/JohnEveryman/' + file
            expected_url = 'https://www.vidble.com/' + file
            self.assertEqual(expected_filename, content.make_filename())

    def check_output(self, content):
        self.assertEqual('https://vidble.com/XOwqxH6Xz9.jpg', content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/XOwqxH6Xz9.jpg', content.make_filename())

    def get_single_soup(self):
        current_file_path = path.dirname(path.abspath(__file__))
        current_file_path = path.join(current_file_path, 'Resources/vidble_single_test.html')
        with open(current_file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')
