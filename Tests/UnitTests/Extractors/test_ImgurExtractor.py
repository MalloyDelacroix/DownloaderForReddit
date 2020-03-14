import unittest
from unittest.mock import patch
import logging

from DownloaderForReddit.Utils.ImgurUtils import ImgurError
from DownloaderForReddit.Extractors.ImgurExtractor import ImgurExtractor
from DownloaderForReddit.Utils import Injector, ImgurUtils, ExtractorUtils
from DownloaderForReddit.Core import Const
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


class TestImgurExtractor(unittest.TestCase):
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

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()
        ImgurUtils.credit_time_limit = 1
        ExtractorUtils.timeout_dict.clear()
        ExtractorUtils.time_limit_dict.clear()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_album')
    def test_extract_content_assignment_album(self, ex_mock):
        ie = ImgurExtractor(self.get_album_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_single')
    def test_extract_content_assignment_single(self, ex_mock):
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_direct_link')
    def test_extract_content_assignment_direct(self, ex_mock):
        ie = ImgurExtractor(self.get_direct_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_album_images')
    def test_extract_album(self, img_mock):
        print(img_mock)
        img_mock.return_value = self.url_extract_dict['ALBUM']
        ie = ImgurExtractor(self.get_album_post(), MockObjects.get_blank_user())
        ie.extract_album()

        img_mock.assert_called_with('Bi63r')
        self.assertTrue(self.check_img_album_output(ie.extracted_content))
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def check_img_album_output(self, content_list):
        count = 1
        for con in content_list:
            if con.url not in self.url_extract_dict['ALBUM']:
                return False
            if not con.make_filename().startswith(
                    'C:/Users/Gorgoth/Downloads/JohnEveryman/') or con.file_ext != '.jpg' or \
                    int(con.number_in_seq) != count:
                return False
            count += 1
        return True

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_extract_single(self, img_mock):
        img_mock.return_value = self.url_extract_dict['SINGLE']
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_single()

        content = ie.extracted_content[0]

        img_mock.assert_called_with('fb2yRj0')
        self.assertEqual(self.url_extract_dict['SINGLE'], content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.jpg', content.make_filename())
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def test_extract_direct(self):
        post = MockObjects.get_generic_mock_post()
        post.url = 'https://imgur.com/fb2yRj0.jpg'

        ie = ImgurExtractor(post, MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual('https://imgur.com/fb2yRj0.jpg', content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.jpg', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.jpg', content.make_filename())
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def test_extract_direct_gif(self):
        post = MockObjects.get_generic_mock_post()
        post.url = 'https://i.imgur.com/mOlfhY3.gif'

        ie = ImgurExtractor(post, MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual('https://i.imgur.com/mOlfhY3.mp4', content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.mp4', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/mOlfhY3.mp4', content.make_filename())
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def test_extract_direct_unknown_ext(self, ):
        post = self.get_direct_post_unknown_ext()
        post.url = 'https://i.imgur.com/fb2yRj0.foo'
        ie = ImgurExtractor(post, MockObjects.get_blank_user())
        ie.extract_direct_link()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Unrecognized extension' in failed_post.status)

    # region Exception Tests

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_down_error(self, img_mock):
        img_mock.side_effect = ImgurError(status_code=500)

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Imgur is currently down' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_client_connection_error_unknown(self, img_mock):
        img_mock.side_effect = ImgurError(status_code=900)

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Unknown Imgur connection error' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_runtime_unknown_error(self, img_mock):
        img_mock.side_effect = RuntimeError()

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        self.assertEqual(1, len(ie.failed_extract_posts))
        failed_post = ie.failed_extract_posts[0]
        print(failed_post.status)
        self.assertEqual('Failed to extract content', failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.check_credits')
    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_single')
    def test_imgur_rate_limit_exceeded_error(self, img_mock, credits_mock):
        TIME = 600000
        img_mock.side_effect = ImgurError(status_code=429)
        credits_mock.return_value = 0

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]

        self.assertEqual('Out of user credits',failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_down_error(self, img_mock):
        img_mock.side_effect = ImgurError(status_code=500)

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]
        print(failed_post.status)
        self.assertEqual('Imgur is currently down', failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_does_not_exist_error(self, img_mock):
        img_mock.side_effect = ImgurError(status_code=404)

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]
        self.assertEqual("Content does not exist.", failed_post.status)
        self.assertFalse(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.get_single_image')
    def test_imgur_failed_to_locate_403_error(self, img_mock):
        img_mock.side_effect = ImgurError(status_code=403)

        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        failed_post = ie.failed_extract_posts[0]
        print(failed_post.status)
        self.assertEqual('Forbidden', failed_post.status)
        self.assertEqual(0, len(ie.failed_extracts_to_save))
    # endregion

    def get_direct_post(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_host_dict['DIRECT']
        return post

    def get_direct_post_gif(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.make_gif_url(self.url_extract_dict['SINGLE'])
        return post

    def get_direct_post_unknown_ext(self):
        post = MockObjects.get_generic_mock_post()
        url = self.url_extract_dict['SINGLE'].rsplit('.', 1)[0]
        post.url = '%s.foo' % url
        return post

    def get_direct_post_mislinked_unknown_ext(self):
        post = MockObjects.get_generic_mock_post()
        url = self.url_host_dict['SINGLE']
        post.url = url + '.foo'
        return post

    def get_single_post(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_host_dict['SINGLE']
        return post

    def get_album_post(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_host_dict['ALBUM']
        return post

    def make_gif_url(self, img):
        url = img.rsplit('.', 1)[0]
        return '%sgif.mp4' % url

    def make_gif_list(self, img_list):
        gif_list = []
        for img in img_list:
            url = img.rsplit('.', 1)[0]
            gif_list.append('%sgif.mp4' % url)
        return gif_list


class MockClientResponse:

    def __init__(self, link=None, type='image/gif', animated=False):
        self.link = link
        self.type = type
        self.animated = animated

    @property
    def mp4(self):
        try:
            url = self.link.rsplit('.', 1)[0]
            return '%sgif.mp4' % url
        except TypeError:
            return None
