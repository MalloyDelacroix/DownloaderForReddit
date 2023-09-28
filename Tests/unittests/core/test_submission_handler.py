from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from Tests.mockobjects import mock_objects
from DownloaderForReddit.core.submission_handler import SubmissionHandler
from DownloaderForReddit.core.errors import Error
from DownloaderForReddit.utils import injector


class TestSubmissionHandler(TestCase):

    PATH = 'DownloaderForReddit.core.submission_handler.SubmissionHandler'

    extractor_dict = {
        'ImgurExtractor': True,
        'GfycatExtractor': True,
        'RedgifsExtractor': True,
        'VidbleExtractor': True,
        'RedditUploadsExtractor': True,
        'RedditVideoExtractor': True,
        'GenericVideoExtractor': False,
        'EromeExtractor': True,
        'SelfPostExtractor': True,
        'DirectExtractor': True,
    }

    @classmethod
    def setUpClass(cls):
        cls.settings = MagicMock()
        cls.settings.extractor_dict = cls.extractor_dict
        injector.settings_manager = cls.settings

    def setUp(self):
        stop_run = MagicMock()
        stop_run.is_set.return_value = False
        self.submission = MagicMock()
        self.post = MagicMock()
        self.mock_queue = MagicMock()
        self.handler = SubmissionHandler(self.submission, self.post, 0, MagicMock(), self.mock_queue, stop_run)

    def tearDown(self):
        self.settings.extractor_dict = self.extractor_dict

    def test_assign_extractor_direct(self):
        post = mock_objects.get_unsupported_direct_post()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('DirectExtractor', ex.__name__)
        self.settings.extractor_dict['DirectExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    def test_assign_extractor_imgur(self):
        post = mock_objects.get_mock_post_imgur()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('ImgurExtractor', ex.__name__)
        self.settings.extractor_dict['ImgurExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    def test_assign_extractor_gfycat(self):
        post = mock_objects.get_mock_post_gfycat()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('GfycatExtractor', ex.__name__)
        self.settings.extractor_dict['GfycatExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    def test_assign_extractor_vidble(self):
        post = mock_objects.get_mock_post_vidble()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('VidbleExtractor', ex.__name__)
        self.settings.extractor_dict['VidbleExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    def test_assign_extractor_reddit_uploads(self):
        post = mock_objects.get_mock_reddit_uploads_post()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('RedditUploadsExtractor', ex.__name__)
        self.settings.extractor_dict['RedditUploadsExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    def test_assign_extractor_reddit_video(self):
        post = mock_objects.get_mock_reddit_video_post()
        ex = self.handler.assign_extractor(post.url)
        self.assertEqual('RedditVideoExtractor', ex.__name__)
        self.settings.extractor_dict['RedditVideoExtractor'] = False
        ex = self.handler.assign_extractor(post.url)
        self.assertIsNone(ex)

    @patch(f'{PATH}.extract_link')
    @patch(f'{PATH}.parse_html_links')
    def test_extract_text_links_single(self, get_links, extract_link):
        url = 'https://gfycat.com/KindlyElderlyCony'
        link = MagicMock()
        link.has_attr.return_value = True
        d = {'href': url}
        link.__getitem__.side_effect = d.__getitem__
        get_links.return_value = [link]

        self.handler.extract_text_links(None)

        extract_link.assert_called_with(url, text_link_extraction=True)

    @patch(f'{PATH}.extract_link')
    @patch(f'{PATH}.parse_html_links')
    def test_extract_text_links_multiple(self, get_links, extract_link):
        urls = ['https://gfycat.com/KindlyElderlyCony', 'https://invalid_site.com/image/3jfd9nlksd.jpg',
                'https://vidble.com/XOwqxH6Xz9.jpg']
        links = []
        for url in urls:
            link = MagicMock()
            link.has_attr.return_value = True
            d = {'href': url}
            link.__getitem__.side_effect = d.__getitem__
            links.append(link)
        get_links.return_value = links

        self.handler.extract_text_links(None)

        calls = []
        count = 1
        for url in urls:
            calls.append(call(url, text_link_extraction=True, count=count))
            count += 1
        extract_link.assert_has_calls(calls)

    @patch(f'{PATH}.finish_extractor')
    @patch(f'{PATH}.assign_extractor')
    def test_extract_link_successful(self, assign, finish):
        url = mock_objects.get_post().url
        extractor = MagicMock()
        extractor_class = MagicMock()
        extractor_class.return_value = extractor
        assign.return_value = extractor_class
        self.handler.extract_link(url, extra_arg='extra')

        assign.assert_called_with(url)
        extractor_class.assert_called_with(self.post, url=url, submission=self.submission, extra_arg='extra')
        finish.assert_called_with(extractor, text_link_extraction=False)

    @patch(f'{PATH}.handle_unsupported_domain')
    @patch(f'{PATH}.finish_extractor')
    @patch(f'{PATH}.assign_extractor')
    def test_extract_link_no_extractor_returned(self, assign, finish, handle_unsupported):
        url = mock_objects.get_post().url
        assign.return_value = None
        self.handler.extract_link(url, extra_arg='extra')

        assign.assert_called_with(url)
        finish.assert_not_called()
        handle_unsupported.assert_called()

    @patch(f'{PATH}.handle_connection_error')
    @patch(f'{PATH}.finish_extractor')
    @patch(f'{PATH}.assign_extractor')
    def test_extract_link_no_extractor_returned(self, assign, finish, handle_connection_error):
        url = mock_objects.get_post().url
        extractor = MagicMock()
        extractor_class = MagicMock()
        extractor_class.return_value = extractor
        assign.return_value = extractor_class
        finish.side_effect = ConnectionError

        self.handler.extract_link(url, extra_arg='extra')

        assign.assert_called_with(url)
        handle_connection_error.assert_called()

    @patch(f'{PATH}.handle_unknown_error')
    @patch(f'{PATH}.finish_extractor')
    @patch(f'{PATH}.assign_extractor')
    def test_extract_link_no_extractor_returned(self, assign, finish, handle_unknown_error):
        url = mock_objects.get_post().url
        extractor = MagicMock()
        extractor_class = MagicMock()
        extractor_class.return_value = extractor
        assign.return_value = extractor_class
        finish.side_effect = AttributeError

        self.handler.extract_link(url, extra_arg='extra')

        assign.assert_called_with(url)
        handle_unknown_error.assert_called()

    def test_finish_extractor_successful(self):
        extractor = MagicMock()
        extractor.failed_extraction = False
        content = MagicMock()
        content.id = 482
        extractor.extracted_content = [content]

        self.handler.finish_extractor(extractor)

        extractor.extract_content.assert_called()
        self.post.set_extracted.assert_called()
        self.post.set_extraction_failed.assert_not_called()
        self.mock_queue.put.assert_called_with(482)

    def test_finish_extractor_unsuccessful(self):
        extractor = MagicMock()
        extractor.failed_extraction = True
        extractor.extraction_error = Error.FAILED_TO_LOCATE
        extractor.failed_extraction_message = 'Extraction failed'

        self.handler.finish_extractor(extractor)

        extractor.extract_content.assert_called()
        self.post.set_extracted.assert_not_called()
        self.post.set_extraction_failed.assert_called_with(Error.FAILED_TO_LOCATE, extractor.failed_extraction_message)
        self.mock_queue.put.assert_not_called()

    def test_finish_extractor_null_extractor_value(self):
        self.handler.finish_extractor(None)
        self.post.set_extracted.assert_not_called()
        self.post.set_extraction_failed.assert_not_called()
        self.mock_queue.put.assert_not_called()
