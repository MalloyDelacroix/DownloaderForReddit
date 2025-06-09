from unittest import TestCase
from unittest.mock import MagicMock, patch

from DownloaderForReddit.extractors.base_extractor import BaseExtractor
from DownloaderForReddit.utils import injector
from DownloaderForReddit.database.models import Comment


class TestDownloadRunner(TestCase):

    PATH = 'DownloaderForReddit.extractors.base_extractor.BaseExtractor'

    @classmethod
    def setUpClass(cls):
        cls.settings = MagicMock()
        injector.settings_manager = cls.settings

    @patch('requests.get')
    def test_successful_json_retrieval(self, get):
        response = MagicMock()
        response.status_code = 200
        json = '{this: is_some_json}'
        response.json.return_value = json
        response.headers = {'Content-Type': 'json'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_json = base_extractor.get_json(url)

        get.assert_called_with(url, timeout=10)
        self.assertEqual(json, response_json)

    @patch(f'{PATH}.handle_failed_extract')
    @patch('requests.get')
    def test_unsuccessful_json_retrieval_bad_status_code(self, get, handle_failed):
        response = MagicMock()
        response.status_code = 404
        json = '{this: is_some_json}'
        response.json.return_value = json
        response.headers = {'Content-Type': 'json'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_json = base_extractor.get_json(url)

        get.assert_called_with(url, timeout=10)
        self.assertIsNone(response_json)
        handle_failed.assert_called()

    @patch(f'{PATH}.handle_failed_extract')
    @patch('requests.get')
    def test_unsuccessful_json_retrieval_no_json_in_response(self, get, handle_failed):
        response = MagicMock()
        response.status_code = 200
        json = 'this is not json'
        response.json.return_value = json
        response.headers = {'Content-Type': 'text'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_json = base_extractor.get_json(url)

        get.assert_called_with(url, timeout=10)
        self.assertIsNone(response_json)
        handle_failed.assert_called()

    @patch('requests.get')
    def test_successful_text_retrieval(self, get):
        response = MagicMock()
        response.status_code = 200
        text = 'this is some text'
        response.text = text
        response.headers = {'Content-Type': 'text'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_text = base_extractor.get_text(url)

        get.assert_called_with(url, timeout=10)
        self.assertEqual(text, response_text)

    @patch(f'{PATH}.handle_failed_extract')
    @patch('requests.get')
    def test_unsuccessful_text_retrieval_bad_status_code(self, get, handle_failed):
        response = MagicMock()
        response.status_code = 500
        text = 'this is some text'
        response.text = text
        response.headers = {'Content-Type': 'text'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_text = base_extractor.get_text(url)

        get.assert_called_with(url, timeout=10)
        self.assertIsNone(response_text)
        handle_failed.assert_called()

    @patch(f'{PATH}.handle_failed_extract')
    @patch('requests.get')
    def test_unsuccessful_text_retrieval_no_text_in_request(self, get, handle_failed):
        response = MagicMock()
        response.status_code = 200
        text = '{type: json}'
        response.text = text
        response.headers = {'Content-Type': 'json'}
        get.return_value = response

        url = MagicMock()
        base_extractor = BaseExtractor(MagicMock())
        response_text = base_extractor.get_text(url)

        get.assert_called_with(url, timeout=10)
        self.assertIsNone(response_text)
        handle_failed.assert_called()

    def test_make_title(self):
        sig_ro = MagicMock()
        sig_ro.post_download_naming_method = '%[title]'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro

        extractor = BaseExtractor(post)
        extractor.comment = None
        title = extractor.make_title()

        self.assertEqual(title, 'Test Post Title')

    def test_make_title_comment_supplied(self):
        sig_ro = MagicMock()
        sig_ro.comment_naming_method = '%[author_name]-comment'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.significant_reddit_object = sig_ro
        comment = MagicMock(spec=Comment)
        comment.author = user
        comment.post = post

        extractor = BaseExtractor(MagicMock())
        extractor.significant_reddit_object = sig_ro
        extractor.comment = comment
        title = extractor.make_title()

        self.assertEqual(title, 'Test User One-comment')

    def test_make_title_media_id_supplied_in_kwargs(self):
        sig_ro = MagicMock()
        sig_ro.post_download_naming_method = '%[media_id]'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro

        extractor = BaseExtractor(post)
        extractor.comment = None
        title = extractor.make_title(media_id='12345')

        self.assertEqual(title, '12345')

    def test_make_directory_for_post_user(self):
        self.settings.user_save_directory = 'path/to/user_save_directory'
        sig_ro = MagicMock()
        sig_ro.name = 'Test User One'
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.custom_post_save_path = None
        sig_ro.object_type = 'USER'
        post = MagicMock()
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        extractor = BaseExtractor(post)
        extractor.comment = None
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'path/to/user_save_directory/Test User One')

    def test_make_directory_for_post_with_custom_path_user(self):
        sig_ro = MagicMock()
        sig_ro.name = 'Test User One'
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.custom_post_save_path = None
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = 'custom_path/to/user_save_directory'
        post = MagicMock()
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        extractor = BaseExtractor(post)
        extractor.comment = None
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'custom_path/to/user_save_directory/Test User One')

    def test_make_directory_for_comment_user(self):
        self.settings.user_save_directory = 'path/to/user_save_directory'
        sig_ro = MagicMock()
        sig_ro.name = 'Test User One'
        sig_ro.comment_save_structure = '%[post_author_name]/Comments/%[post_title]'
        sig_ro.custom_comment_save_path = None
        sig_ro.object_type = 'USER'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        comment = MagicMock(spec=Comment)
        comment.author = user
        comment.post = post

        extractor = BaseExtractor(post)
        extractor.comment = comment
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'path/to/user_save_directory/Test User One/Comments/Test Post Title')

    def test_make_directory_for_comment_with_custom_path_user(self):
        sig_ro = MagicMock()
        sig_ro.name = 'Test User One'
        sig_ro.comment_save_structure = '%[post_author_name]/Comments/%[post_title]'
        sig_ro.custom_comment_save_path = None
        sig_ro.object_type = 'USER'
        sig_ro.custom_comment_save_path = 'custom_comment_path/to/user_save_directory'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        comment = MagicMock(spec=Comment)
        comment.author = user
        comment.post = post

        extractor = BaseExtractor(post)
        extractor.comment = comment
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'custom_comment_path/to/user_save_directory/Test User One/Comments/Test Post Title')

    def test_make_directory_for_post_subreddit(self):
        self.settings.subreddit_save_directory = 'path/to/subreddit_save_directory'
        sig_ro = MagicMock()
        sig_ro.name = 'Test Subreddit One'
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.custom_post_save_path = None
        sig_ro.object_type = 'SUBREDDIT'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.significant_reddit_object = sig_ro
        post.author = user

        extractor = BaseExtractor(post)
        extractor.comment = None
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'path/to/subreddit_save_directory/Test User One')

    def test_make_directory_for_post_with_custom_path_subreddit(self):
        sig_ro = MagicMock()
        sig_ro.name = 'Test Subreddit One'
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.custom_post_save_path = None
        sig_ro.object_type = 'SUBREDDIT'
        user = MagicMock()
        user.name = 'Test User One'
        sig_ro.custom_post_save_path = 'custom_path/to/subreddit_save_directory'
        post = MagicMock()
        post.significant_reddit_object = sig_ro
        post.author = user

        extractor = BaseExtractor(post)
        extractor.comment = None
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'custom_path/to/subreddit_save_directory/Test User One')

    def test_make_directory_for_comment_subreddit(self):
        self.settings.subreddit_save_directory = 'path/to/subreddit_save_directory'
        sig_ro = MagicMock()
        sig_ro.name = 'Test subreddit One'
        sig_ro.comment_save_structure = '%[post_author_name]/Comments/%[post_title]'
        sig_ro.custom_comment_save_path = None
        sig_ro.object_type = 'SUBREDDIT'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro
        post.author = user
        comment = MagicMock(spec=Comment)
        comment.author = user
        comment.post = post

        extractor = BaseExtractor(post)
        extractor.comment = comment
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'path/to/subreddit_save_directory/Test User One/Comments/Test Post Title')

    def test_make_directory_for_comment_with_custom_path_subreddit(self):
        sig_ro = MagicMock()
        sig_ro.name = 'Test subreddit One'
        sig_ro.comment_save_structure = '%[post_author_name]/Comments/%[post_title]'
        sig_ro.custom_comment_save_path = None
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_comment_save_path = 'custom_comment_path/to/subreddit_save_directory'
        user = MagicMock()
        user.name = 'Test User One'
        post = MagicMock()
        post.title = 'Test Post Title'
        post.sanitized_title = post.title
        post.significant_reddit_object = sig_ro
        post.author = user
        comment = MagicMock(spec=Comment)
        comment.author = user
        comment.post = post

        extractor = BaseExtractor(post)
        extractor.comment = comment
        dir_path = extractor.make_dir_path()

        self.assertEqual(dir_path, 'custom_comment_path/to/subreddit_save_directory/Test User One/Comments/Test Post Title')
