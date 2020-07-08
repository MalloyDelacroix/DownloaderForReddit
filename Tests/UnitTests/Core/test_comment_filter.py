from unittest import TestCase
from unittest.mock import MagicMock

from Tests.mockobjects.MockObjects import get_user
from DownloaderForReddit.core.comment_filter import CommentFilter
from DownloaderForReddit.database.model_enums import CommentDownload, LimitOperator
from DownloaderForReddit.utils import injector


class TestCommentHandler(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = MagicMock()
        injector.settings_manager = cls.settings

    def setUp(self):
        self.filter = CommentFilter()

    def test_filter_extraction_non_submitter_all_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_do_not_extract_do_download(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_do_not_extract_or_download_do_download_content(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_do_not_download_any(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_download_author_only_no_others(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_download_content_author_only_no_other(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_non_submitter_download_all_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_all_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_do_not_extract_do_download(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_do_not_extract_or_download_do_download_content(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_do_not_download_any(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertFalse(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_download_submitter_only_no_others(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_extract_submitter_only_no_others(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_download_content_submitter_only_no_others(self):
        user = get_user(
            extract_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_download_all(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_extraction_submitter_download_all_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_extraction(comment, user))

    def test_filter_download_non_submitter_download_all(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertTrue(self.filter.filter_download(comment, user))

    def test_filter_download_non_submitter_do_not_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_download(comment, user))

    def test_filter_download_non_submitter_download_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_download(comment, user))

    def test_filter_download_submitter_download_all(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_download(comment, user))

    def test_filter_download_submitter_do_not_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DO_NOT_DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertFalse(self.filter.filter_download(comment, user))

    def test_filter_download_submitter_download_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD_ONLY_AUTHOR,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_download(comment, user))

    def test_filter_content_download_non_submitter_download_all(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertTrue(self.filter.filter_content_download(comment, user))

    def test_filter_content_download_non_submitter_do_not_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_content_download(comment, user))

    def test_filter_content_download_non_submitter_download_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = False
        self.assertFalse(self.filter.filter_content_download(comment, user))

    def test_filter_content_download_submitter_download_all(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_content_download(comment, user))

    def test_filter_content_download_submitter_do_not_download(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DO_NOT_DOWNLOAD
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertFalse(self.filter.filter_content_download(comment, user))

    def test_filter_content_download_submitter_download_author_only(self):
        user = get_user(
            extract_comments=CommentDownload.DOWNLOAD,
            download_comments=CommentDownload.DOWNLOAD,
            download_comment_content=CommentDownload.DOWNLOAD_ONLY_AUTHOR
        )
        comment = MagicMock()
        comment.is_submitter = True
        self.assertTrue(self.filter.filter_content_download(comment, user))

    def test_filter_by_score_no_limit_restriction(self):
        user = get_user(comment_score_limit_operator=LimitOperator.NO_LIMIT, comment_score_limit=1000)
        comment = MagicMock()

        comment.score = 2000
        self.assertTrue(self.filter.filter_score_limit(comment, user))

        comment.score = 1000
        self.assertTrue(self.filter.filter_score_limit(comment, user))

        comment.score = 500
        self.assertTrue(self.filter.filter_score_limit(comment, user))

    def test_filter_by_score_greater_than(self):
        user = get_user(comment_score_limit_operator=LimitOperator.GREATER_THAN, comment_score_limit=1000)
        comment = MagicMock()

        comment.score = 2000
        self.assertTrue(self.filter.filter_score_limit(comment, user))

        comment.score = 1000
        self.assertTrue(self.filter.filter_score_limit(comment, user))

        comment.score = 500
        self.assertFalse(self.filter.filter_score_limit(comment, user))

    def test_filter_by_score_less_than(self):
        user = get_user(comment_score_limit_operator=LimitOperator.LESS_THAN, comment_score_limit=1000)
        comment = MagicMock()

        comment.score = 2000
        self.assertFalse(self.filter.filter_score_limit(comment, user))

        comment.score = 1000
        self.assertTrue(self.filter.filter_score_limit(comment, user))

        comment.score = 500
        self.assertTrue(self.filter.filter_score_limit(comment, user))
