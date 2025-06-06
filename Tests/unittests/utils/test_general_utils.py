from unittest import TestCase
from unittest.mock import patch, call

from DownloaderForReddit.utils import general_utils
from Tests.mockobjects.mock_objects import get_content


class TestGeneralUtils(TestCase):

    def setUp(self):
        self.content = get_content()

    @patch('DownloaderForReddit.utils.general_utils.os.path.exists')
    @patch('DownloaderForReddit.utils.system_util.create_directory')
    def test_ensure_content_download_path_no_additional_number(self, mock_create_directory, mock_exists):
        mock_exists.return_value = False

        download_title = general_utils.ensure_content_download_path(self.content)

        self.assertEqual(download_title, self.content.download_title)
        mock_create_directory.assert_called_with(self.content.directory_path)
        mock_exists.assert_called_with(f'{self.content.directory_path}/{self.content.download_title}.{self.content.extension}')

    @patch('DownloaderForReddit.utils.general_utils.os.path.exists')
    @patch('DownloaderForReddit.utils.system_util.create_directory')
    def test_ensure_content_download_path_existing_path(self, mock_create_directory, mock_exists):
        mock_exists.side_effect = [True, True, True, False]

        download_title = general_utils.ensure_content_download_path(self.content)

        self.assertEqual(download_title, f'{self.content.download_title}(3)')
        mock_create_directory.assert_called_with(self.content.directory_path)
        expected_calls = [
            call(f'{self.content.directory_path}/{self.content.download_title}.{self.content.extension}'),
            call(f'{self.content.directory_path}/{self.content.download_title}(1).{self.content.extension}'),
            call(f'{self.content.directory_path}/{self.content.download_title}(2).{self.content.extension}'),
            call(f'{self.content.directory_path}/{self.content.download_title}(3).{self.content.extension}')
        ]
        self.assertEqual(mock_exists.call_args_list, expected_calls)

    @patch('DownloaderForReddit.utils.general_utils.logger.error')
    @patch('DownloaderForReddit.utils.system_util.create_directory')
    def test_ensure_content_download_path_permission_error(self, mock_create_dir, mock_log_error):
        mock_create_dir.side_effect = PermissionError

        download_title = general_utils.ensure_content_download_path(self.content)

        self.assertEqual(download_title, self.content.download_title)
        mock_log_error.assert_called_with(
            f'Could not create directory path', extra={'directory_path': self.content.directory_path}, exc_info=True
        )
