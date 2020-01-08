import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

from DownloaderForReddit.Extractors.VidbleExtractor import VidbleExtractor
from DownloaderForReddit.Utils import Injector
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


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

    @patch('DownloaderForReddit.Extractors.VidbleExtractor.get_json')
    def test_extract_album(self,j_mock):
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


    @patch('DownloaderForReddit.Extractors.VidbleExtractor.extract_direct_link')
    def test_extract_content_assignment_direct(self, es_mock):
        post = MockObjects.get_mock_post_vidble()
        post.url = self.extracted_single_url_explore
        ve = VidbleExtractor(post, MockObjects.get_blank_user())
        ve.extract_content()

        es_mock.assert_called()

    def check_output_album(self,contents):
        filenames = ["lkPvqs0yh5.png",
             "F5DgE2O64b.gif",
             "XOwqxH6Xz9.jpg",
             "3a4xNLuO9M.png"
        ]
        for content, file in zip(contents,filenames):
            self.assertEqual('Picture(s)', content.post_title)
            self.assertEqual('Pics', content.subreddit)
            self.assertEqual(1521473630, content.date_created)
            expected_filename = 'C:/Users/Gorgoth/Downloads/JohnEveryman/' + file
            self.assertEqual(expected_filename, content.filename)

    def check_output(self, content):
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/toqeUzXBIl.jpg', content.filename)

    def get_single_soup_show(self):
        with open('Tests/UnitTests/Extractors/Resources/vidble_single_test_show.html', 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')

    def get_single_soup_explore(self):
        with open('Tests/UnitTests/Extractors/Resources/vidble_single_test_explore.html', 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')
