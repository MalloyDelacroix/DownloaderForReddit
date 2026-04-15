from unittest import TestCase
from unittest.mock import patch, MagicMock, PropertyMock
import logging
import prawcore

from DownloaderForReddit.core.search_handler import SearchHandler
from DownloaderForReddit.utils import injector


logging.disable(logging.CRITICAL)


class TestSearchHandler(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings_manager = MagicMock()
        cls.settings_manager.search_fallback_post_limit = 100
        cls.settings_manager.search_fallback_threshold = 3
        injector.settings_manager = cls.settings_manager

    def setUp(self):
        self.reddit_instance = MagicMock()
        self.search_handler = SearchHandler(self.reddit_instance)

    # =========================================================================
    # Tests for should_use_fallback()
    # =========================================================================

    def test_should_use_fallback_disabled_globally(self):
        """Fallback should not trigger when global setting is disabled."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=0,
            user_setting=None,
            global_setting=False
        )
        self.assertFalse(result)

    def test_should_use_fallback_enabled_globally_below_threshold(self):
        """Fallback should trigger when enabled and profile returns fewer posts than threshold."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=2,
            user_setting=None,
            global_setting=True
        )
        self.assertTrue(result)

    def test_should_use_fallback_enabled_globally_at_threshold(self):
        """Fallback should not trigger when profile returns exactly threshold posts."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=3,  # equals threshold
            user_setting=None,
            global_setting=True
        )
        self.assertFalse(result)

    def test_should_use_fallback_enabled_globally_above_threshold(self):
        """Fallback should not trigger when profile returns more than threshold posts."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=10,
            user_setting=None,
            global_setting=True
        )
        self.assertFalse(result)

    def test_should_use_fallback_user_override_enables(self):
        """User setting True should override global False."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=0,
            user_setting=True,
            global_setting=False
        )
        self.assertTrue(result)

    def test_should_use_fallback_user_override_disables(self):
        """User setting False should override global True."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=0,
            user_setting=False,
            global_setting=True
        )
        self.assertFalse(result)

    def test_should_use_fallback_zero_posts_triggers(self):
        """Fallback should trigger when profile returns zero posts."""
        result = self.search_handler.should_use_fallback(
            profile_post_count=0,
            user_setting=None,
            global_setting=True
        )
        self.assertTrue(result)

    # =========================================================================
    # Tests for verify_author()
    # =========================================================================

    def test_verify_author_matching(self):
        """Should return True when author matches expected username."""
        submission = MagicMock()
        submission.author.name = 'TestUser'
        result = self.search_handler.verify_author(submission, 'TestUser')
        self.assertTrue(result)

    def test_verify_author_case_insensitive(self):
        """Author matching should be case-insensitive."""
        submission = MagicMock()
        submission.author.name = 'TestUser'
        result = self.search_handler.verify_author(submission, 'testuser')
        self.assertTrue(result)

    def test_verify_author_non_matching(self):
        """Should return False when author doesn't match."""
        submission = MagicMock()
        submission.author.name = 'OtherUser'
        result = self.search_handler.verify_author(submission, 'TestUser')
        self.assertFalse(result)

    def test_verify_author_deleted(self):
        """Should return False when author is deleted (None)."""
        submission = MagicMock()
        submission.author = None
        result = self.search_handler.verify_author(submission, 'TestUser')
        self.assertFalse(result)

    def test_verify_author_no_name_attribute(self):
        """Should return False when author has no name attribute."""
        submission = MagicMock()
        del submission.author.name
        result = self.search_handler.verify_author(submission, 'TestUser')
        self.assertFalse(result)

    # =========================================================================
    # Tests for search_user_submissions()
    # =========================================================================

    def test_search_user_submissions_success(self):
        """Should yield submissions from search results."""
        mock_submissions = [MagicMock() for _ in range(3)]
        for i, sub in enumerate(mock_submissions):
            sub.author.name = 'TestUser'
            sub.id = f'sub{i}'

        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = iter(mock_submissions)
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser', limit=10))

        self.assertEqual(3, len(results))
        self.reddit_instance.subreddit.assert_called_once_with('all')
        mock_subreddit.search.assert_called_once_with(
            'author:TestUser',
            sort='new',
            time_filter='all',
            limit=10
        )

    def test_search_user_submissions_filters_wrong_author(self):
        """Should filter out submissions from other authors."""
        mock_sub1 = MagicMock()
        mock_sub1.author.name = 'TestUser'
        mock_sub2 = MagicMock()
        mock_sub2.author.name = 'OtherUser'  # Wrong author
        mock_sub3 = MagicMock()
        mock_sub3.author.name = 'TestUser'

        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = iter([mock_sub1, mock_sub2, mock_sub3])
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser'))

        self.assertEqual(2, len(results))
        self.assertNotIn(mock_sub2, results)

    def test_search_user_submissions_uses_default_limit(self):
        """Should use settings default when limit not specified."""
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = iter([])
        self.reddit_instance.subreddit.return_value = mock_subreddit

        list(self.search_handler.search_user_submissions('TestUser'))

        mock_subreddit.search.assert_called_once_with(
            'author:TestUser',
            sort='new',
            time_filter='all',
            limit=100  # From settings_manager mock
        )

    def test_search_user_submissions_rate_limit(self):
        """Should handle rate limit exception gracefully."""
        mock_subreddit = MagicMock()
        mock_subreddit.search.side_effect = prawcore.exceptions.TooManyRequests(MagicMock())
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser'))

        self.assertEqual(0, len(results))

    def test_search_user_submissions_request_exception(self):
        """Should handle request exception gracefully."""
        mock_subreddit = MagicMock()
        mock_subreddit.search.side_effect = prawcore.exceptions.RequestException(
            MagicMock(), MagicMock(), MagicMock()
        )
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser'))

        self.assertEqual(0, len(results))

    def test_search_user_submissions_prawcore_exception(self):
        """Should handle generic prawcore exception gracefully."""
        mock_subreddit = MagicMock()
        mock_subreddit.search.side_effect = prawcore.exceptions.PrawcoreException()
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser'))

        self.assertEqual(0, len(results))

    def test_search_user_submissions_empty_results(self):
        """Should handle empty search results."""
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = iter([])
        self.reddit_instance.subreddit.return_value = mock_subreddit

        results = list(self.search_handler.search_user_submissions('TestUser'))

        self.assertEqual(0, len(results))
