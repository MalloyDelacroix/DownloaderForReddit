from unittest import TestCase
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from DownloaderForReddit.core.download.downloader import Downloader
from DownloaderForReddit.database.models import Content, BaseModel
from DownloaderForReddit.utils import injector, general_utils


class TestDownloader(TestCase):

    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database
        cls.engine = create_engine('sqlite:///:memory:')
        BaseModel.metadata.create_all(cls.engine)  # Create tables
        cls.Session = sessionmaker(bind=cls.engine)
        cls._original_ensure_content_download_path = general_utils.ensure_content_download_path
        general_utils.ensure_content_download_path = MagicMock(return_value='path/to/file')

    @classmethod
    def tearDownClass(cls):
        general_utils.ensure_content_download_path = cls._original_ensure_content_download_path

    def setUp(self):
        self.session = self.Session()
        self.mock_settings_manager = MagicMock(
            use_multi_part_downloader=False,
            multi_part_threshold=1024 * 1024
        )
        injector.settings_manager = self.mock_settings_manager
        self.mock_stop_run = MagicMock()
        self.mock_stop_run.is_set.return_value = False
        self.downloader = Downloader(download_queue=[], download_session_id=123, stop_run=self.mock_stop_run)
        self.downloader.db = MagicMock()  # Mock db interface
        self.downloader.db.get_scoped_session.return_value.__enter__.return_value = self.session
        self.downloader.check_headers = MagicMock(return_value={})

        # Insert some test data
        self.duplicate_hash = 'abcd1234'
        self.content1 = Content(md5_hash=self.duplicate_hash)
        self.content2 = Content(md5_hash='xyz9876')
        self.content3 = Content(
            url="http://example.com/file",
            title="example",
            extension="txt",
            directory_path="/mock/path"
        )
        self.session.add_all([self.content1, self.content2, self.content3])
        self.session.commit()
        self.multi_part_limit = 1024 * 1024 * 10

    def tearDown(self):
        self.session.close()

    def setup_mock_downloader_methods(self):
        """
        Replaces most of the methods in the downloader with mocks.  This is done in order to test the download method
        while able to control feedback and avoid side effects.
        """
        self.downloader.should_use_multi_part = MagicMock()
        self.downloader.download_with_multipart = MagicMock()
        self.downloader.should_use_hash = MagicMock()
        self.downloader.download_with_hash = MagicMock()
        self.downloader.download_without_hash = MagicMock()
        self.downloader.finish_download = MagicMock()
        self.downloader.is_duplicate_hash = MagicMock()
        self.downloader.handle_duplicate_content = MagicMock()
        self.downloader.handle_date_modified = MagicMock()
        self.downloader.output_downloaded_message = MagicMock()
        self.downloader.get_downloaded_output_data = MagicMock()
        self.downloader.handle_download_stopped = MagicMock()
        self.downloader.finish_multi_part_download = MagicMock()
        self.downloader.handle_unsuccessful_response = MagicMock()
        self.downloader.handle_connection_error = MagicMock()
        self.downloader.handle_unknown_error = MagicMock()
        self.downloader.handle_deleted_content_error = MagicMock()

    def test_should_use_multi_part_when_conditions_are_met(self):
        self.mock_settings_manager.use_multi_part_downloader = True
        self.mock_settings_manager.multi_part_threshold = 1000

        result = self.downloader.should_use_multi_part(file_size=2000)

        self.assertTrue(result)

    def test_should_use_multi_part_when_disabled(self):
        self.mock_settings_manager.use_multi_part_downloader = False
        self.mock_settings_manager.multi_part_threshold = 1000

        result = self.downloader.should_use_multi_part(file_size=2000)

        self.assertFalse(result)

    def test_should_use_multi_part_when_file_size_is_below_threshold(self):
        self.mock_settings_manager.use_multi_part_downloader = True
        self.mock_settings_manager.multi_part_threshold = 1000

        result = self.downloader.should_use_multi_part(file_size=500)

        self.assertFalse(result)

    def test_should_use_hash_true(self):
        content = MagicMock()
        content.post.significant_reddit_object.hash_duplicates = True
        self.assertTrue(self.downloader.should_use_hash(content))

    def test_should_use_hash_false(self):
        content = MagicMock()
        content.post.significant_reddit_object.hash_duplicates = False
        self.assertFalse(self.downloader.should_use_hash(content))

    def test_is_duplicate_hash_exists(self):
        # Test when a hash exists in the database
        result = self.downloader.is_duplicate_hash(self.duplicate_hash)
        self.assertTrue(result)

    def test_is_duplicate_hash_not_exists(self):
        # Test when a hash does not exist in the database
        result = self.downloader.is_duplicate_hash('nonexistent_hash')
        self.assertFalse(result)

    def test_is_duplicate_hash_empty(self):
        # Test behavior when an empty string is provided as the hash
        result = self.downloader.is_duplicate_hash('')
        self.assertFalse(result)

    def test_finish_download_non_hashed_successful(self):
        self.content1.md5_hash = None
        self.downloader.handle_duplicate_content = MagicMock()
        self.downloader.handle_date_modified = MagicMock()
        self.downloader.output_downloaded_message = MagicMock()
        self.downloader.handle_download_stopped = MagicMock()

        self.downloader.finish_download(self.content1)

        self.downloader.handle_duplicate_content.assert_not_called()
        self.downloader.handle_date_modified.assert_called_once_with(self.content1)
        self.downloader.output_downloaded_message.assert_called_once_with(self.content1)
        self.downloader.handle_download_stopped.assert_not_called()

    def test_finish_download_non_hashed_hard_stop(self):
        self.content1.md5_hash = None
        self.downloader.handle_duplicate_content = MagicMock()
        self.downloader.handle_date_modified = MagicMock()
        self.downloader.output_downloaded_message = MagicMock()
        self.downloader.handle_download_stopped = MagicMock()

        self.downloader.hard_stop = True
        self.downloader.finish_download(self.content1)

        self.downloader.handle_duplicate_content.assert_not_called()
        self.downloader.handle_date_modified.assert_not_called()
        self.downloader.output_downloaded_message.assert_not_called()
        self.downloader.handle_download_stopped.assert_called_once_with(self.content1)

    def test_finish_download_hashed_non_duplicate_successful(self):
        self.content1.md5_hash = 'a0uqlka0f9'
        self.downloader.is_duplicate_hash = MagicMock(return_value=False)
        self.downloader.handle_duplicate_content = MagicMock()
        self.downloader.handle_date_modified = MagicMock()
        self.downloader.output_downloaded_message = MagicMock()
        self.downloader.handle_download_stopped = MagicMock()

        self.downloader.finish_download(self.content1)

        self.downloader.handle_duplicate_content.assert_not_called()
        self.downloader.handle_date_modified.assert_called_once_with(self.content1)
        self.downloader.output_downloaded_message.assert_called_once_with(self.content1)
        self.downloader.handle_download_stopped.assert_not_called()

    def test_finish_download_hashed_duplicate_successful(self):
        self.content1.md5_hash = 'a0uqlka0f9'
        self.downloader.is_duplicate_hash = MagicMock(return_value=True)
        self.downloader.handle_duplicate_content = MagicMock()
        self.downloader.handle_date_modified = MagicMock()
        self.downloader.output_downloaded_message = MagicMock()
        self.downloader.handle_download_stopped = MagicMock()

        self.downloader.finish_download(self.content1)

        self.downloader.handle_duplicate_content.assert_called_once_with(self.content1)
        self.downloader.handle_date_modified.assert_not_called()
        self.downloader.output_downloaded_message.assert_not_called()
        self.downloader.handle_download_stopped.assert_not_called()

    @patch('DownloaderForReddit.utils.system_util.delete_file')
    @patch('DownloaderForReddit.messaging.message.Message.send_debug')
    def test_handle_duplicate_content_remove(self, mock_send_debug, mock_delete_file):
        content = MagicMock(spec=Content)
        content.get_full_file_path.return_value = '/path/to/file'
        content.url = 'http://example.com/file'

        self.downloader.download_count = 0
        self.downloader.duplicate_count = 0
        self.mock_settings_manager.remove_duplicates_on_download = True
        self.downloader.get_downloaded_output_data = MagicMock(return_value="Sample Output Data")

        self.downloader.handle_duplicate_content(content)

        mock_delete_file.assert_called_once_with('/path/to/file')
        mock_send_debug.assert_called_once_with(
            'Duplicate file deleted: Sample Output Data\nhttp://example.com/file'
        )
        self.assertEqual(self.downloader.duplicate_count, 1)
        self.assertEqual(self.downloader.download_count, 0)

    @patch('DownloaderForReddit.messaging.message.Message.send_debug')
    def test_handle_duplicate_content_save(self, mock_send_debug):
        content = MagicMock(spec=Content)
        content.url = 'http://example.com/file'

        self.downloader.download_count = 0
        self.downloader.duplicate_count = 0
        self.downloader.settings_manager.remove_duplicates_on_download = False
        self.downloader.get_downloaded_output_data = MagicMock(return_value="Sample Output Data")
        self.downloader.handle_date_modified = MagicMock()

        self.downloader.handle_duplicate_content(content)

        mock_send_debug.assert_called_once_with(
            'Duplicate file saved: Sample Output Data'
        )
        content.set_downloaded.assert_called_once_with(self.downloader.download_session_id)
        self.assertEqual(self.downloader.duplicate_count, 1)
        self.assertEqual(self.downloader.download_count, 1)

    @patch('DownloaderForReddit.core.download.downloader.requests.get')
    def test_download_successful(self, mock_get):
        self.setup_mock_downloader_methods()
        self.downloader.should_use_multi_part.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': self.multi_part_limit - 100}
        mock_get.return_value = mock_response
        self.downloader.download(content_id=self.content3.id)

        mock_get.assert_called_once_with(self.content3.url, stream=True, timeout=10, headers={})
        self.downloader.finish_download.assert_called_once_with(self.content3)

    @patch('DownloaderForReddit.core.download.downloader.requests.get')
    def test_download_with_small_file(self, mock_get):
        self.setup_mock_downloader_methods()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': '512'}
        mock_get.return_value = mock_response

        self.downloader.download(content_id=self.content3.id)

        self.downloader.finish_download.assert_not_called()
        self.downloader.handle_deleted_content_error.assert_called_once_with(self.content3)

    @patch('DownloaderForReddit.core.download.downloader.requests.get')
    def test_download_unsuccessful_response(self, mock_get):
        self.setup_mock_downloader_methods()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.downloader.download(content_id=self.content3.id)

        self.downloader.handle_unsuccessful_response.assert_called_once_with(self.content3, 404)
        self.downloader.finish_download.assert_not_called()


    @patch('DownloaderForReddit.core.download.downloader.requests.get')
    def test_download_connection_error(self, mock_get):
        self.setup_mock_downloader_methods()
        mock_get.side_effect = ConnectionError

        self.downloader.download(content_id=self.content3.id)

        self.downloader.handle_connection_error.assert_called_once_with(self.content3)

    @patch('DownloaderForReddit.core.download.downloader.requests.get')
    def test_download_unknown_error(self, mock_get):
        self.setup_mock_downloader_methods()
        mock_get.side_effect = Exception

        self.downloader.download(content_id=self.content3.id)

        self.downloader.handle_unknown_error.assert_called_once_with(self.content3)
