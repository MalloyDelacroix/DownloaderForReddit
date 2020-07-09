from unittest import TestCase
from unittest.mock import MagicMock, patch

from DownloaderForReddit.extractors.base_extractor import BaseExtractor
from DownloaderForReddit.utils import injector
from DownloaderForReddit.database.database_handler import DatabaseHandler
from Tests.mockobjects.mock_objects import get_post


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
