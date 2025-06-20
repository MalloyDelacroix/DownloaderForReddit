from unittest import TestCase
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from DownloaderForReddit.core.duplicate_handler import DuplicateHandler
from DownloaderForReddit.database.model_enums import DuplicateControlMethod
from DownloaderForReddit.database.models import BaseModel, Content, User, Post
from DownloaderForReddit.utils import injector
from Tests.mockobjects.mock_objects import get_content, get_user, get_post


class TestDuplicateHandlerIsDuplicate(TestCase):

    """
    This class is only to test the `is_duplicate` method of the `DuplicateHandler` class.  It is separated because,
    unlike the other method tests in the DuplicateHandler class, it relies on an in-memory database being made in order
    to query duplicate hashes.  This should reduce the overhead in the tests that don't need the database created.
    """

    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database
        cls.engine = create_engine('sqlite:///:memory:')
        BaseModel.metadata.create_all(cls.engine)  # Create tables
        cls.Session = sessionmaker(bind=cls.engine)
        mock_db_manager = MagicMock()
        mock_db_manager.get_scoped_session.return_value.__enter__.return_value = cls.Session()
        injector.database_handler = mock_db_manager

    def setUp(self):
        self.session = self.Session()
        self.mock_settings_manager = MagicMock()
        injector.settings_manager = self.mock_settings_manager
        self.user = get_user(
            post_download_naming_method='%[title]',
            post_save_structure='%[author_name]',
            duplicate_naming_method='%[title] - duplicate',
            duplicate_save_structure='%[author_name]/Duplicates'
        )
        self.post = get_post(user=self.user)
        self.content = get_content(post=self.post, user=self.user)
        self.duplicate_hash = '123asdf123'
        self.original_content = Content(md5_hash='non_dup_hash')
        self.duplicate_content = Content(md5_hash=self.duplicate_hash)
        self.session.add_all([self.original_content, self.duplicate_content])
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_is_duplicate_false(self):
        content = MagicMock(spec=Content)
        content.md5_hash = '098lkj098'

        self.assertFalse(DuplicateHandler.is_duplicate(content))

    def test_is_duplicate_true(self):
        content = MagicMock(spec=Content)
        content.md5_hash = self.duplicate_hash

        self.assertTrue(DuplicateHandler.is_duplicate(content))

    def test_is_duplicate_no_md5_hash_value(self):
        content = MagicMock(spec=Content)
        content.md5_hash = None

        self.assertFalse(DuplicateHandler.is_duplicate(content))


class TestDuplicateHandlerHandleDuplicate(TestCase):

    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.delete_duplicate')
    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.rename_duplicate')
    def test_handle_duplicate_keep(self, mock_rename_duplicate, mock_delete_duplicate):
        user = MagicMock(spec=User)
        user.duplicate_control_method = DuplicateControlMethod.KEEP
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.post = post

        dup_handler = DuplicateHandler(content)
        dup_handler.handle_duplicate()

        mock_rename_duplicate.assert_not_called()
        mock_delete_duplicate.assert_not_called()

    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.delete_duplicate')
    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.rename_duplicate')
    def test_handle_duplicate_delete(self, mock_rename_duplicate, mock_delete_duplicate):
        user = MagicMock(spec=User)
        user.duplicate_control_method = DuplicateControlMethod.DELETE
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.post = post

        dup_handler = DuplicateHandler(content)
        dup_handler.handle_duplicate()

        mock_rename_duplicate.assert_not_called()
        mock_delete_duplicate.assert_called_once()

    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.delete_duplicate')
    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.rename_duplicate')
    def test_handle_duplicate_move(self, mock_rename_duplicate, mock_delete_duplicate):
        user = MagicMock(spec=User)
        user.duplicate_control_method = DuplicateControlMethod.MOVE
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.post = post

        dup_handler = DuplicateHandler(content)
        dup_handler.handle_duplicate()

        mock_rename_duplicate.assert_called_once()
        mock_delete_duplicate.assert_not_called()

    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.delete_duplicate')
    @patch('DownloaderForReddit.core.duplicate_handler.DuplicateHandler.rename_duplicate')
    def test_handle_duplicate_control_method_null(self, mock_rename_duplicate, mock_delete_duplicate):
        user = MagicMock(spec=User)
        user.duplicate_control_method = None
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.post = post

        dup_handler = DuplicateHandler(content)
        dup_handler.handle_duplicate()

        mock_rename_duplicate.assert_not_called()
        mock_delete_duplicate.assert_not_called()

    @patch('DownloaderForReddit.messaging.message.Message.send_info')
    @patch('DownloaderForReddit.utils.system_util.delete_file')
    def test_delete_duplicate(self, mock_delete_file, mock_send_info):
        user = MagicMock(spec=User)
        user.name = 'Test User'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.user = user
        content.post = post
        content.title = 'Test Title'
        content.url = 'http://example.com/file'
        content.get_full_file_path.return_value = 'path/to/file/Test Title.mp4'

        dup_handler = DuplicateHandler(content)
        dup_handler.delete_duplicate()

        mock_delete_file.assert_called_once_with('path/to/file/Test Title.mp4')
        mock_send_info.assert_called_once_with(
            f'Duplicate deleted: Test User: Test Title'
        )

    @patch('DownloaderForReddit.utils.general_utils.ensure_file_path')
    @patch('DownloaderForReddit.core.duplicate_handler.FilenameGenerator')
    @patch('DownloaderForReddit.core.duplicate_handler.os.rename')
    def test_rename_duplicate(self, mock_rename, mock_filename_generator_class, mock_ensure_file_path):
        mock_filename_generator = MagicMock()
        mock_filename_generator_class.return_value = mock_filename_generator
        mock_filename_generator.make_dir_path.return_value = 'base/path'
        mock_filename_generator.make_title.return_value = 'mock title'
        mock_ensure_file_path.side_effect = lambda x: x  # Return the input value unchanged

        user = MagicMock(spec=User)
        user.name = 'Test User'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = user
        content = MagicMock(spec=Content)
        content.post = post
        content.title = 'Test Title'
        content.url = 'http://example.com/file'
        content.extension = 'mp4'
        content.get_full_file_path.return_value = 'path/to/file/Test Title.mp4'

        dup_handler = DuplicateHandler(content)
        dup_handler.rename_duplicate()
        mock_rename.assert_called_once_with(
            'path/to/file/Test Title.mp4',
            'base/path/mock title.mp4'
        )
        mock_ensure_file_path.assert_called_once_with('base/path/mock title.mp4')
