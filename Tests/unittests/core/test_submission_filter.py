from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from DownloaderForReddit.core.submission_filter import SubmissionFilter
from DownloaderForReddit.database.model_enums import *
from Tests.mockobjects.mock_objects import MockPrawSubmission, get_user


class MyTestCase(TestCase):

    def setUp(self):
        self.sub_filter = SubmissionFilter()

    def test_score_filter_no_limit_restriction(self):
        user = get_user(post_score_limit_operator=LimitOperator.NO_LIMIT, post_score_limit=1000)
        submission = MockPrawSubmission(score=2000)
        f = self.sub_filter.score_filter(submission, user)
        self.assertTrue(f)

        submission.score = 500
        self.assertTrue(self.sub_filter.score_filter(submission, user))

    def test_score_filter_greater_than(self):
        user = get_user(post_score_limit_operator=LimitOperator.GREATER_THAN, post_score_limit=1000)
        submission = MockPrawSubmission(score=2000)
        self.assertTrue(self.sub_filter.score_filter(submission, user))

        submission.score = 1000
        self.assertTrue(self.sub_filter.score_filter(submission, user))

        submission.score = 500
        self.assertFalse(self.sub_filter.score_filter(submission, user))

    def test_score_filter_less_than(self):
        user = get_user(post_score_limit_operator=LimitOperator.LESS_THAN, post_score_limit=1000)
        submission = MockPrawSubmission(score=500)
        self.assertTrue(self.sub_filter.score_filter(submission, user))

        submission.score = 1000
        self.assertTrue(self.sub_filter.score_filter(submission, user))

        submission.score = 2000
        self.assertFalse(self.sub_filter.score_filter(submission, user))

    def test_nsfw_filter_include(self):
        user = get_user(download_nsfw=NsfwFilter.INCLUDE)
        submission = MockPrawSubmission(over_18=True)
        self.assertTrue(self.sub_filter.nsfw_filter(submission, user))

        submission.over_18 = False
        self.assertTrue(self.sub_filter.nsfw_filter(submission, user))

    def test_nsfw_filter_exclude(self):
        user = get_user(download_nsfw=NsfwFilter.EXCLUDE)
        submission = MockPrawSubmission(over_18=False)
        self.assertTrue(self.sub_filter.nsfw_filter(submission, user))

        submission.over_18 = True
        self.assertFalse(self.sub_filter.nsfw_filter(submission, user))

    def test_nsfw_filter_only(self):
        user = get_user(download_nsfw=NsfwFilter.ONLY)
        submission = MockPrawSubmission(over_18=True)
        self.assertTrue(self.sub_filter.nsfw_filter(submission, user))

        submission.over_18 = False
        self.assertFalse(self.sub_filter.nsfw_filter(submission, user))

    def test_date_filter_absolute_limit(self):
        limit = datetime.now() - timedelta(days=10)
        date = datetime.now() - timedelta(days=5)
        user = get_user(absolute_date_limit=limit, date_limit=None)
        submission = MockPrawSubmission(created=date)
        self.assertTrue(self.sub_filter.date_filter(submission, user))

        submission.created = (date - timedelta(days=20)).timestamp()
        self.assertFalse(self.sub_filter.date_filter(submission, user))

    def test_date_filter_date_limit(self):
        limit = datetime.now() - timedelta(days=10)
        date = datetime.now() - timedelta(days=13)
        user = get_user(absolute_date_limit=limit, date_limit=limit - timedelta(days=5))
        submission = MockPrawSubmission(created=date)
        self.assertTrue(self.sub_filter.date_filter(submission, user))

        submission.created = (date - timedelta(days=10)).timestamp()
        self.assertFalse(self.sub_filter.date_filter(submission, user))

    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.date_filter')
    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.nsfw_filter')
    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.score_filter')
    def test_master_submission_filter_passing(self, score, nsfw, date):
        score.return_value = True
        nsfw.return_value = True
        date.return_value = True
        self.assertTrue(self.sub_filter.filter_submission(None, None))
        score.assert_called()
        nsfw.assert_called()
        date.assert_called()

    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.date_filter')
    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.nsfw_filter')
    @patch('DownloaderForReddit.core.submission_filter.SubmissionFilter.score_filter')
    def test_master_submission_filter_failing(self, score, nsfw, date):
        score.return_value = True
        nsfw.return_value = False
        date.return_value = True
        self.assertFalse(self.sub_filter.filter_submission(None, None))
        score.assert_called()
        nsfw.assert_called()
