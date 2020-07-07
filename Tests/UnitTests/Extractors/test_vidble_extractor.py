from os import path
from unittest.mock import patch

from bs4 import BeautifulSoup

from .abstract_extractor_test import ExtractorTest
from Tests.mockobjects.MockObjects import (get_post, get_mock_post_vidble, get_mock_post_vidible_album,
                                           get_mock_post_vidble_direct)
from DownloaderForReddit.extractors.vidble_extractor import VidbleExtractor


@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_dir_path')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_title')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.check_duplicate_content')
class TestVidbleExtractor(ExtractorTest):

    PATH = 'DownloaderForReddit.extractors.vidble_extractor.VidbleExtractor'

    @patch(f'{PATH}.get_imgs')
    def test_extract_single_show(self, s_mock, check_duplicate, make_title, make_dir_path):
        s_mock.return_value = self.get_single_soup()
        out_url = 'https://vidble.com/XOwqxH6Xz9.jpg'
        post = get_mock_post_vidble(session=self.session)
        check_duplicate.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ve = VidbleExtractor(post)
        ve.extract_single()

        self.check_output(ve, out_url, post)

    @patch(f'{PATH}.get_imgs')
    def test_extract_single_explore(self, s_mock, check_duplicate, make_title, make_dir_path):
        s_mock.return_value = self.get_single_soup()
        out_url = 'https://vidble.com/XOwqxH6Xz9.jpg'
        post = get_post(session=self.session, url='https://vidble.com/explore/XOwqxH6Xz9')
        check_duplicate.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ve = VidbleExtractor(post)
        ve.extract_single()

        self.check_output(ve, out_url, post)

    @patch(f'{PATH}.get_json')
    def test_extract_album(self, j_mock, check_duplicate, make_title, make_dir_path):
        post = get_mock_post_vidible_album(session=self.session)
        out_urls = [
            "https://www.vidble.com/lkPvqs0yh5.png",
            "https://www.vidble.com/F5DgE2O64b.gif",
            "https://www.vidble.com/XOwqxH6Xz9.jpg",
            "https://www.vidble.com/3a4xNLuO9M.png"
        ]
        links = [
            "//www.vidble.com/lkPvqs0yh5_med.png",
            "//www.vidble.com/F5DgE2O64b.gif",
            "//www.vidble.com/XOwqxH6Xz9_med.jpg",
            "//www.vidble.com/3a4xNLuO9M_med.png"
        ]
        j_mock.return_value = {"pics": links}
        check_duplicate.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ve = VidbleExtractor(post)
        ve.extract_album()

        self.check_output_multiple(ve, out_urls, post)

    @patch(f'{PATH}.extract_single')
    def test_extract_content_assignment_single_show(self, es_mock, check_duplicate, make_title, make_dir_path):
        post = get_mock_post_vidble()

        ve = VidbleExtractor(post)
        ve.extract_content()

        es_mock.assert_called()

    @patch(f'{PATH}.extract_single')
    def test_extract_content_assignment_single_explore(self, es_mock, check_duplicate, make_title, make_dir_path):
        post = get_post(url='https://vidble.com/explore/XOwqxH6Xz9')

        ve = VidbleExtractor(post)
        ve.extract_content()

        es_mock.assert_called()

    @patch(f'{PATH}.extract_direct_link')
    def test_extract_content_explore_direct(self, es_mock, check_duplicate, make_title, make_dir_path):
        post = get_post(url='https://vidble.com/explore/XOwqxH6Xz9.jpg')
        ve = VidbleExtractor(post)
        ve.extract_content()

        self.assertEqual('https://vidble.com/XOwqxH6Xz9.jpg', ve.url)
        es_mock.assert_called()

    @patch(f'{PATH}.extract_direct_link')
    def test_extract_content_assignment_direct(self, es_mock, check_duplicate, make_title, make_dir_path):
        post = get_mock_post_vidble_direct()
        ve = VidbleExtractor(post)
        ve.extract_content()

        es_mock.assert_called()

    def get_single_soup(self):
        current_file_path = path.dirname(path.abspath(__file__))
        current_file_path = path.join(current_file_path, 'Resources/vidble_single_test.html')
        with open(current_file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all('img')
