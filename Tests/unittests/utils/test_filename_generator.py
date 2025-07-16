from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.database.models import Comment, Post, Content, User, Subreddit
from DownloaderForReddit.utils import injector
from DownloaderForReddit.utils.filename_generator import FilenameGenerator


class TestFilenameGenerator(TestCase):

    def setUp(self):
        self.user_dir = 'test_user_save_directory'
        self.sub_dir = 'test_subreddit_save_directory'
        self.mock_settings = MagicMock(
            user_save_directory=self.user_dir,
            subreddit_save_directory=self.sub_dir,
        )
        injector.settings_manager = self.mock_settings

    def test_is_setup_correctly_post_comment_supplied(self):
        comment = MagicMock(spec=Comment)
        sig_ro = MagicMock(spec=User)
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        comment.post = post
        self.assertTrue(isinstance(comment, Comment))

        filename_generator = FilenameGenerator(comment)
        self.assertEqual(post, filename_generator.post)
        self.assertEqual(sig_ro, filename_generator.reddit_object)
        self.assertEqual(comment, filename_generator.comment)
        self.assertEqual(comment, filename_generator.title_obj)

    def test_is_setup_correctly_post_supplied(self):
        sig_ro = MagicMock(spec=User)
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        self.assertTrue(isinstance(post, Post))

        filename_generator = FilenameGenerator(post)
        self.assertEqual(post, filename_generator.post)
        self.assertEqual(sig_ro, filename_generator.reddit_object)
        self.assertIsNone(filename_generator.comment)
        self.assertEqual(post, filename_generator.title_obj)

    def test_is_setup_correctly_content_supplied(self):
        sig_ro = MagicMock(spec=User)
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        content = MagicMock(spec=Content)
        content.post = post

        filename_generator = FilenameGenerator(content)
        self.assertEqual(post, filename_generator.post)
        self.assertEqual(sig_ro, filename_generator.reddit_object)
        self.assertIsNone(filename_generator.comment)
        self.assertEqual(post, filename_generator.title_obj)

    def test_make_title_using_post_title(self):
        post = MagicMock(spec=Post)
        post.author = MagicMock()
        post.author.name = 'Test Author'
        post.sanitized_title = 'Test Post Title'
        post.significant_reddit_object.post_download_naming_method = '%[title]'

        filename_generator = FilenameGenerator(post)
        title = filename_generator.make_title()
        self.assertEqual('Test Post Title', title)

    def test_make_title_using_post_author_name(self):
        post = MagicMock(spec=Post)
        post.author = MagicMock()
        post.author.name = 'Test Author'
        post.sanitized_title = 'Test Post Title'
        post.significant_reddit_object.post_download_naming_method = '%[post_author_name]'

        filename_generator = FilenameGenerator(post)
        title = filename_generator.make_title()
        self.assertEqual('Test Author', title)

    def test_make_title_using_post_author_name_and_post_title(self):
        post = MagicMock(spec=Post)
        post.author = MagicMock()
        post.author.name = 'Test Author'
        post.sanitized_title = 'Test Post Title'
        post.significant_reddit_object.post_download_naming_method = '%[post_author_name] - %[title]'

        filename_generator = FilenameGenerator(post)
        title = filename_generator.make_title()
        self.assertEqual('Test Author - Test Post Title', title)

    def test_make_title_using_comment(self):
        comment = MagicMock(spec=Comment)
        comment.author = MagicMock()
        comment.author.name = 'Test Comment Author'
        comment.post = MagicMock()
        comment.post.author = MagicMock()
        comment.post.author.name = 'Test Post Author'
        comment.post.sanitized_title = 'Test Post Title'
        comment.post.significant_reddit_object.comment_naming_method = '%[author_name]-comment'

        filename_generator = FilenameGenerator(comment)
        title = filename_generator.make_title()
        self.assertEqual('Test Comment Author-comment', title)

    def test_make_title_using_comment_and_post_title(self):
        comment = MagicMock(spec=Comment)
        comment.author = MagicMock()
        comment.author.name = 'Test Comment Author'
        comment.post = MagicMock()
        comment.post.author = MagicMock()
        comment.post.author.name = 'Test Post Author'
        comment.post.sanitized_title = 'Test Post Title'
        comment.post.significant_reddit_object.comment_naming_method = '%[post_title] - %[author_name]-comment'

        filename_generator = FilenameGenerator(comment)
        title = filename_generator.make_title()
        self.assertEqual('Test Post Title - Test Comment Author-comment', title)

    def test_make_title_using_post_title_is_duplicate(self):
        post = MagicMock(spec=Post)
        post.author = MagicMock()
        post.author.name = 'Duplicate Author'
        post.sanitized_title = 'Duplicate Post Title'
        post.significant_reddit_object.duplicate_naming_method = '%[title] - duplicate'

        filename_generator = FilenameGenerator(post, is_duplicate=True)
        title = filename_generator.make_title()
        self.assertEqual('Duplicate Post Title - duplicate', title)

    def test_make_title_using_post_author_name_is_duplicate(self):
        post = MagicMock(spec=Post)
        post.author = MagicMock()
        post.author.name = 'Duplicate Author'
        post.sanitized_title = 'Duplicate Post Title'
        post.significant_reddit_object.duplicate_naming_method = '%[author_name] - duplicate'

        filename_generator = FilenameGenerator(post, is_duplicate=True)
        title = filename_generator.make_title()
        self.assertEqual('Duplicate Author - duplicate', title)

    def test_make_dir_path_for_post_using_authors_name(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = None
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        filename_generator = FilenameGenerator(post)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.user_dir}/Test Author', dir_path)

    def test_make_dir_path_for_post_using_authors_name_subreddit(self):
        sig_ro = MagicMock(spec=Subreddit)
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_post_save_path = None
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.name = 'Test Subreddit'
        author = MagicMock(spec=User)
        author.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        filename_generator = FilenameGenerator(post)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.sub_dir}/Test Subreddit', dir_path)

    def test_make_dir_path_for_post_using_authors_name_and_post_score(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = None
        sig_ro.post_save_structure = '%[author_name]-%[post_score]'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        post.score = 1234

        filename_generator = FilenameGenerator(post)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.user_dir}/Test Author-1234', dir_path)

    def test_make_dir_path_for_post_using_authors_name_and_post_score_subreddit(self):
        sig_ro = MagicMock(spec=Subreddit)
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_post_save_path = None
        sig_ro.post_save_structure = '%[author_name]-%[post_score]'
        sig_ro.name = 'Test Subreddit'
        author = MagicMock(spec=User)
        author.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        post.score = 1234

        filename_generator = FilenameGenerator(post)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.sub_dir}/Test Subreddit-1234', dir_path)

    def test_make_dir_path_for_post_using_custom_save_path(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = 'custom_post_save_path'
        sig_ro.post_save_structure = '%[author_name]'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        filename_generator = FilenameGenerator(post)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'custom_post_save_path/Test Author', dir_path)

    def test_make_dir_path_for_comment_using_authors_name(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_comment_save_path = None
        sig_ro.comment_save_structure = '%[author_name]/comments'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = sig_ro

        filename_generator = FilenameGenerator(comment)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.user_dir}/Test Author/comments', dir_path)

    def test_make_dir_path_for_comment_using_custom_save_path_and_authors_name(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_comment_save_path = 'custom_comment_save_path'
        sig_ro.comment_save_structure = '%[author_name]/comments'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = sig_ro

        filename_generator = FilenameGenerator(comment)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'custom_comment_save_path/Test Author/comments', dir_path)

    def test_make_dir_path_for_comment_from_subreddit(self):
        sig_ro = MagicMock(spec=Subreddit)
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_comment_save_path = None
        sig_ro.comment_save_structure = '%[author_name]/comments'
        sig_ro.name = 'Test Subreddit'
        user = MagicMock(spec=User)
        user.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = user

        filename_generator = FilenameGenerator(comment)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.sub_dir}/Test Author/comments', dir_path)

    def test_make_dir_path_for_comment_from_subreddit_using_custom_save_path(self):
        sig_ro = MagicMock(spec=Subreddit)
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_comment_save_path = 'custom_comment_save_path_sub'
        sig_ro.comment_save_structure = '%[author_name]/comments'
        sig_ro.name = 'Test Subreddit'
        user = MagicMock(spec=User)
        user.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = user

        filename_generator = FilenameGenerator(comment)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'custom_comment_save_path_sub/Test Author/comments', dir_path)

    def test_make_dir_path_for_duplicate_user_post(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = None
        sig_ro.duplicate_save_structure = '%[author_name]/Duplicates'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        filename_generator = FilenameGenerator(post, is_duplicate=True)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.user_dir}/Test Author/Duplicates', dir_path)

    def test_make_dir_path_for_duplicate_user_post_with_custom_save_path(self):
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_post_save_path = 'custom_post_save_path'
        sig_ro.duplicate_save_structure = '%[author_name]/Duplicates'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro

        filename_generator = FilenameGenerator(post, is_duplicate=True)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'custom_post_save_path/Test Author/Duplicates', dir_path)

    def test_make_dir_path_for_duplicate_user_comment(self):
        """
        Comment save structure will be ignored if the content is a duplicate.
        """
        sig_ro = MagicMock(spec=User)
        sig_ro.object_type = 'USER'
        sig_ro.custom_comment_save_path = None
        sig_ro.comment_save_structure = '%[post_title]/comments'
        sig_ro.duplicate_save_structure = '%[author_name]/Duplicates'
        sig_ro.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        post.author = sig_ro
        post.title = 'Test Post Title'
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = sig_ro

        filename_generator = FilenameGenerator(comment, is_duplicate=True)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.user_dir}/Test Author/Duplicates', dir_path)

    def test_make_dir_path_for_duplicate_subreddit_comment(self):
        sig_ro = MagicMock(spec=Subreddit)
        sig_ro.object_type = 'SUBREDDIT'
        sig_ro.custom_comment_save_path = None
        sig_ro.comment_save_structure = '%[post_title]/comments'
        sig_ro.duplicate_save_structure = '%[author_name]/Duplicates'
        sig_ro.name = 'Test Subreddit'
        user = MagicMock(spec=User)
        user.name = 'Test Author'
        post = MagicMock(spec=Post)
        post.significant_reddit_object = sig_ro
        comment = MagicMock(spec=Comment)
        comment.post = post
        comment.author = user

        filename_generator = FilenameGenerator(comment, is_duplicate=True)
        dir_path = filename_generator.make_dir_path()
        self.assertEqual(f'{self.sub_dir}/Test Author/Duplicates', dir_path)
