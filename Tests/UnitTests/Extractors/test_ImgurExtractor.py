import unittest
from unittest.mock import patch
import logging
from imgurpython.helpers.error import ImgurClientError

from DownloaderForReddit.Extractors.ImgurExtractor import ImgurExtractor
from DownloaderForReddit.Utils import Injector, ImgurUtils, ExtractorUtils
from DownloaderForReddit.Core import Const
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


class TestImgurExtractor(unittest.TestCase):

    url_host_dict = {
        'SINGLE': 'https://imgur.com/fb2yRj0',
        'ALBUM': 'https://imgur.com/a/Bi63r'
    }

    url_extract_dict = {
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

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_album(self, img_mock):
        img_mock.get_album_images.return_value = [MockClientResponse(link=url) for url in self.url_extract_dict['ALBUM']]
        ie = ImgurExtractor(self.get_album_post(), MockObjects.get_blank_user())
        ie.extract_album()

        self.assertTrue(self.check_img_album_output(ie.extracted_content))
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def check_img_album_output(self, content_list):
        count = 1
        for con in content_list:
            if con.url not in self.url_extract_dict['ALBUM']:
                return False
            if not con.filename.startswith('C:/Users/Gorgoth/Downloads/JohnEveryman/') or con.file_ext != '.jpg' or \
                    int(con.number_in_seq) != count:
                return False
            count += 1
        return True

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_gif_album(self, img_mock):
        img_mock.get_album_images.return_value = [MockClientResponse(link=url, animated=True)
                                                  for url in self.url_extract_dict['ALBUM']]
        ie = ImgurExtractor(self.get_album_post(), MockObjects.get_blank_user())
        ie.extract_album()

        self.assertTrue(self.check_img_gif_album_output(ie.extracted_content))
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    def check_img_gif_album_output(self, content_list):
        count = 1
        for con in content_list:
            if con.url not in self.make_gif_list(self.url_extract_dict['ALBUM']):
                return False
            if not con.filename.startswith('C:/Users/Gorgoth/Downloads/JohnEveryman/') or con.file_ext != '.mp4' or \
                    int(con.number_in_seq) != count:
                return False
            count += 1
        return True

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_single_base(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.url_extract_dict['SINGLE'])
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_single()

        content = ie.extracted_content[0]
        self.assertEqual(self.url_extract_dict['SINGLE'], content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.jpg', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_single_gif(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.url_extract_dict['SINGLE'], animated=True)
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_single()
        content = ie.extracted_content[0]

        self.assertEqual(content.url, self.make_gif_url(self.url_extract_dict['SINGLE']))
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.mp4', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.mp4', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.url_extract_dict['SINGLE'])
        ie = ImgurExtractor(self.get_direct_post(), MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual(self.url_extract_dict['SINGLE'], content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.jpg', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.jpg', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct_gif(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.make_gif_url(self.url_extract_dict['SINGLE']),
                                                             animated=True)
        ie = ImgurExtractor(self.get_direct_post_gif(), MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.mp4', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0gif.mp4', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct_unknown_ext(self, img_mock):
        ie = ImgurExtractor(self.get_direct_post_unknown_ext(), MockObjects.get_blank_user())
        ie.extract_direct_link()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Unrecognized extension' in failed_post.status)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct_mislinked(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.url_host_dict['SINGLE'] + '.jpg')
        ie = ImgurExtractor(self.get_direct_post_mislinked(), MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual(self.url_extract_dict['SINGLE'], content.url)
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.jpg', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0.jpg', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct_gif_mislinked(self, img_mock):
        img_mock.get_image.return_value = MockClientResponse(link=self.make_gif_url(self.url_extract_dict['SINGLE']),
                                                             animated=True)
        ie = ImgurExtractor(self.get_direct_post_mislinked_gif(), MockObjects.get_blank_user())
        ie.extract_direct_link()

        content = ie.extracted_content[0]
        self.assertEqual('Picture(s)', content.post_title)
        self.assertEqual('Pics', content.subreddit)
        self.assertEqual('.mp4', content.file_ext)
        self.assertEqual(1521473630, content.date_created)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/fb2yRj0gif.mp4', content.filename)
        self.assertTrue(len(ie.failed_extract_posts) == 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_direct_mislinked_unknown_ext(self, img_mock):
        ie = ImgurExtractor(self.get_direct_post_mislinked_unknown_ext(), MockObjects.get_blank_user())
        ie.extract_direct_link()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Unrecognized extension' in failed_post.status)

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_album')
    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_content_assignment_album(self, img_mock, ex_mock):
        ie = ImgurExtractor(self.get_album_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_single')
    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_content_assignment_single(self, img_mock, ex_mock):
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_direct_link')
    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_content_assignment_direct(self, img_mock, ex_mock):
        ie = ImgurExtractor(self.get_direct_post(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    @patch('DownloaderForReddit.Extractors.ImgurExtractor.extract_direct_link')
    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_extract_content_assignment_direct_mislinked(self, img_mock, ex_mock):
        ie = ImgurExtractor(self.get_direct_post_mislinked(), MockObjects.get_blank_user())
        ie.extract_content()

        ex_mock.assert_called()

    # region Exception Tests

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    @patch('DownloaderForReddit.Utils.ImgurUtils.get_client')
    def test_imgur_client_connection_over_cap_error(self, img_mock, util_mock):
        img_mock.side_effect = ImgurClientError(status_code=500, error_message='Over capacity')
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Imgur is currently over capacity' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    @patch('DownloaderForReddit.Utils.ImgurUtils.get_client')
    def test_imgur_client_connection_error_unknown(self, img_mock, util_mock):
        img_mock.side_effect = ImgurClientError(status_code=900, error_message='Unknown')
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Unknown imgur connection error' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    @patch('DownloaderForReddit.Utils.ImgurUtils.get_client')
    def test_imgur_client_unknown_error_on_setup(self, img_mock, util_mock):
        img_mock.side_effect = RuntimeError()
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Failed to connect to imgur.com' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_rate_limit_exceeded_error_with_remaining_credits(self, img_mock):
        with unittest.mock.patch('DownloaderForReddit.Utils.ImgurUtils.get_new_client', return_value=img_mock):
            img_mock.get_image.side_effect = ImgurClientError(status_code=429, error_message='error')
            img_mock.credits = {'UserRemaining': 400}
            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            failed_post = ie.failed_extract_posts[0]
            self.assertTrue('rate limit exceeded' in failed_post.status)
            self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_rate_limit_exceeded_error_no_remaining_credits(self, img_mock):
        with unittest.mock.patch('DownloaderForReddit.Utils.ImgurUtils.get_new_client', return_value=img_mock):
            TIME = 600000
            img_mock.get_image.side_effect = ImgurClientError(status_code=429, error_message='error')
            img_mock.credits = {'UserRemaining': 0, 'UserReset': TIME}
            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            failed_post = ie.failed_extract_posts[0]
            self.assertTrue('Out of user credits' in failed_post.status)
            self.assertTrue(len(ie.failed_extracts_to_save) > 0)
            self.assertTrue(ImgurUtils.credit_time_limit == TIME)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_rate_limit_exceeded_credit_dict_is_null(self, img_mock):
        with unittest.mock.patch('DownloaderForReddit.Utils.ImgurUtils.get_new_client', return_value=img_mock):
            img_mock.get_image.side_effect = ImgurClientError(status_code=429, error_message='error')
            img_mock.credits = {'UserRemaining': None}
            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            failed_post = ie.failed_extract_posts[0]
            self.assertTrue('rate limit exceeded' in failed_post.status)
            self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    #@patch('DownloaderForReddit.Utils.ImgurUtils.get_new_client',lambda *args: DownloaderForReddit.Utils.ImgurUtils.imgur_client)
    def test_multiple_imgur_rate_limit_exceeded_with_timeout_dict(self, img_mock):
        with unittest.mock.patch('DownloaderForReddit.Utils.ImgurUtils.get_new_client', return_value=img_mock):
            img_mock.get_image.side_effect = ImgurClientError(status_code=429, error_message='error')
            img_mock.credits = {'UserRemaining': None}
            increment = Const.TIMEOUT_INCREMENT
            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            self.assertEqual(ExtractorUtils.time_limit_dict[type(ie).__name__], increment)
            increment += Const.TIMEOUT_INCREMENT

            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            self.assertEqual(ExtractorUtils.time_limit_dict[type(ie).__name__], increment)
            increment += Const.TIMEOUT_INCREMENT

            ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
            ie.extract_content()
            self.assertEqual(ExtractorUtils.time_limit_dict[type(ie).__name__], increment)


    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_no_credit_error(self, img_mock):
        img_mock.get_image.side_effect = ImgurClientError(status_code=403, error_message='error')
        img_mock.credits = {'ClientRemaining': 0}
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Not enough imgur credits to extract post' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_over_capacity_error(self, img_mock):
        img_mock.get_image.side_effect = ImgurClientError(status_code=500, error_message='Over capacity')
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('over capacity' in failed_post.status)
        self.assertTrue(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_does_not_exist_error(self, img_mock):
        img_mock.get_image.side_effect = ImgurClientError(status_code=404, error_message='error')
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Content does not exist' in failed_post.status)
        self.assertFalse(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_failed_to_locate_403_error(self, img_mock):
        img_mock.get_image.side_effect = ImgurClientError(status_code=403, error_message='error')
        img_mock.credits = {'ClientRemaining': None}
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Failed to locate content' in failed_post.status)
        self.assertFalse(len(ie.failed_extracts_to_save) > 0)

    @patch('DownloaderForReddit.Utils.ImgurUtils.imgur_client')
    def test_imgur_failed_to_locate_general(self, img_mock):
        img_mock.get_image.side_effect = ImgurClientError(status_code=403, error_message='error')
        img_mock.credits = {'ClientRemaining': 900}
        ie = ImgurExtractor(self.get_single_post(), MockObjects.get_blank_user())
        ie.extract_content()
        failed_post = ie.failed_extract_posts[0]
        self.assertTrue('Failed to locate content' in failed_post.status)
        self.assertFalse(len(ie.failed_extracts_to_save) > 0)

    # endregion

    def get_direct_post(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_extract_dict['SINGLE']
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

    def get_direct_post_mislinked(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_host_dict['SINGLE'] + '.jpg'
        return post

    def get_direct_post_mislinked_gif(self):
        post = MockObjects.get_generic_mock_post()
        post.url = self.url_host_dict['SINGLE'] + 'gif.gifv'
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
