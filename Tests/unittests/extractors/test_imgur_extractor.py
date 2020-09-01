from unittest.mock import patch

from .abstract_extractor_test import ExtractorTest
from Tests.mockobjects.mock_objects import get_post
from DownloaderForReddit.utils.imgur_utils import ImgurError
from DownloaderForReddit.extractors.imgur_extractor import ImgurExtractor


@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_dir_path')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_title')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.filter_content')
class TestImgurExtractor(ExtractorTest):
    PATH = 'DownloaderForReddit.extractors.imgur_extractor.ImgurExtractor'
    UTILS = 'DownloaderForReddit.utils.imgur_utils'

    url_host_dict = {
        'DIRECT': 'https://imgur.com/fb2yRj0.jpg',
        'DIRECT_GIF': 'https://i.imgur.com/mOlfhY3.gif',
        'SINGLE': 'https://imgur.com/fb2yRj0',
        'ALBUM': 'https://imgur.com/a/Bi63r'
    }

    url_extract_dict = {
        'DIRECT': 'https://imgur.com/fb2yRj0.jpg',
        'DIRECT_GIF': 'https://i.imgur.com/mOlfhY3.mp4',
        'SINGLE': 'https://i.imgur.com/fb2yRj0.jpg',
        'ALBUM': ['https://i.imgur.com/Zjn7rJ0.jpg',
                  'https://i.imgur.com/2de2HlU.jpg',
                  'https://i.imgur.com/rpJtk5n.jpg',
                  'https://i.imgur.com/pw22DCf.jpg',
                  'https://i.imgur.com/NuBKzX0.jpg',
                  'https://i.imgur.com/QMu5OtK.jpg',
                  'https://i.imgur.com/tbG00Oa.jpg']
    }

    @patch(f'{PATH}.extract_album')
    def test_extract_content_assignment_album(self, ex_mock, filter_content, make_title, make_dir_path):
        ie = ImgurExtractor(self.get_album_post())
        ie.extract_content()

        ex_mock.assert_called()

    @patch(f'{PATH}.extract_single')
    def test_extract_content_assignment_single(self, ex_mock, filter_content, make_title, make_dir_path):
        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        ex_mock.assert_called()

    @patch(f'{PATH}.extract_direct_link')
    def test_extract_content_assignment_direct(self, ex_mock, filter_content, make_title, make_dir_path):
        post = get_post()
        post.url = 'https://imgur.com/fb2yRj0.jpg'
        ie = ImgurExtractor(post)
        ie.extract_content()

        ex_mock.assert_called()

    @patch(f'{UTILS}.get_album_images')
    def test_extract_album(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.return_value = self.url_extract_dict['ALBUM']
        post = self.get_album_post()
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ie = ImgurExtractor(post)
        ie.extract_album()

        img_mock.assert_called_with('Bi63r')
        self.check_output_multiple(ie, self.url_extract_dict['ALBUM'], post)

    @patch(f'{UTILS}.get_single_image')
    def test_extract_single(self, img_mock, filter_content, make_title, make_dir_path):
        post = get_post(url='https://imgur.com/fb2yRj0', session=self.session)
        url = 'https://i.imgur.com/fb2yRj0.jpg'
        img_mock.return_value = url
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ie = ImgurExtractor(post)
        ie.extract_single()

        img_mock.assert_called_with('fb2yRj0')
        self.check_output(ie, url, post)

    def test_extract_direct(self, filter_content, make_title, make_dir_path):
        url = 'https://imgur.com/fb2yRj0.jpg'
        post = get_post(url=url, session=self.session)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ie = ImgurExtractor(post)
        ie.extract_direct_link()

        self.check_output(ie, url, post)

    def test_extract_question(self, filter_content, make_title, make_dir_path):
        in_url = 'https://imgur.com/fb2yRj0.jpg?125'
        out_url = 'https://imgur.com/fb2yRj0.jpg'
        post = get_post(url=in_url, session=self.session)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ie = ImgurExtractor(post)
        ie.extract_direct_link()

        self.check_output(ie, out_url, post)

    def test_extract_direct_gif(self, filter_content, make_title, make_dir_path):
        in_url = 'https://i.imgur.com/mOlfhY3.gif'
        out_url = 'https://i.imgur.com/mOlfhY3.mp4'
        post = get_post(url=in_url, session=self.session)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ie = ImgurExtractor(post)
        ie.extract_direct_link()

        self.check_output(ie, out_url, post)

    def test_extract_direct_unknown_ext(self, filter_content, make_title, make_dir_path):
        post = get_post(url='https://i.imgur.com/fb2yRj0.foo')
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'
        ie = ImgurExtractor(post)
        ie.extract_direct_link()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))

    # region Exception Tests

    @patch(f'{UTILS}.get_single_image')
    def test_imgur_down_error(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = ImgurError(status_code=500)

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('over capacity' in ie.failed_extraction_message.lower())

    @patch(f'{UTILS}.get_single_image')
    def test_imgur_client_connection_error_unknown(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = ImgurError(status_code=900)

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('connection error' in ie.failed_extraction_message.lower())

    @patch(f'{UTILS}.get_single_image')
    def test_imgur_runtime_unknown_error(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = RuntimeError()

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('failed to extract content' in ie.failed_extraction_message.lower())

    @patch(f'{UTILS}.check_credits')
    @patch(f'{PATH}.extract_single')
    def test_imgur_rate_limit_exceeded_error(self, img_mock, credits_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = ImgurError(status_code=429)
        credits_mock.return_value = 0

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('out of user credits' in ie.failed_extraction_message.lower())

    @patch(f'{UTILS}.get_single_image')
    def test_imgur_does_not_exist_error(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = ImgurError(status_code=404)

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('does not exist' in ie.failed_extraction_message.lower())

    @patch(f'{UTILS}.get_single_image')
    def test_imgur_failed_to_locate_403_error(self, img_mock, filter_content, make_title, make_dir_path):
        img_mock.side_effect = ImgurError(status_code=403)

        ie = ImgurExtractor(self.get_single_post())
        ie.extract_content()

        self.assertTrue(ie.failed_extraction)
        self.assertIsNotNone(ie.failed_extraction_message)
        self.assertEqual(0, len(ie.extracted_content))
        self.assertTrue('forbidden' in ie.failed_extraction_message.lower())

    # endregion

    def get_single_post(self):
        post = get_post(url=self.url_host_dict['SINGLE'], session=self.session)
        return post

    def get_album_post(self):
        post = get_post(url=self.url_host_dict['ALBUM'], session=self.session)
        return post
