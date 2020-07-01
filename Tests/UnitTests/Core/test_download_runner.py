from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
import logging
from datetime import datetime, timedelta

from DownloaderForReddit.core.download_runner import DownloadRunner
from DownloaderForReddit.database.database_handler import DatabaseHandler
from DownloaderForReddit.database.models import User, Subreddit, Post
from DownloaderForReddit.utils import injector
from Tests.mockobjects.MockObjects import MockPrawPost, get_blank_user, get_blank_subreddit


logging.disable(logging.CRITICAL)
DL = 'DownloaderForReddit.core.download_runner.DownloadRunner'


@patch('DownloaderForReddit.utils.reddit_utils.get_reddit_instance', return_value=None)
class TestDownloadRunner(TestCase):

    def submission_generator(self, submission_list):
        """
        Helper list to turn a list of mock praw posts into a generator similar to what is returned from praw when
        extracting submissions from reddit.
        :param submission_list: A list of mock submissions.
        :return: A generator of the supplied mock submissions.
        """
        for x in submission_list:
            yield x

    @classmethod
    def setUpClass(cls):
        cls.now = datetime.now()
        cls.settings_manager = MagicMock()
        injector.settings_manager = cls.settings_manager
        injector.database_handler = DatabaseHandler(in_memory=True)

    @patch(f'{DL}.get_subreddit_submissions')
    @patch(f'{DL}.get_user_submissions')
    @patch(f'{DL}.get_reddit_object_submissions')
    def test_setup_for_user_download(self, get_ro_submissions, get_user_submissions, get_sub_submissions, reddit_utils):
        download_runner = DownloadRunner(user_id_list=[2, 3, 4])
        download_runner.run_download()
        get_ro_submissions.assert_not_called()
        get_user_submissions.assert_called()
        get_sub_submissions.assert_not_called()

    @patch(f'{DL}.get_subreddit_submissions')
    @patch(f'{DL}.get_user_submissions')
    @patch(f'{DL}.get_reddit_object_submissions')
    def test_setup_for_subreddit_download(self, get_ro_submissions, get_user_submissions, get_sub_submissions,
                                          reddit_utils):
        download_runner = DownloadRunner(subreddit_id_list=[2, 3, 4])
        download_runner.run_download()
        get_ro_submissions.assert_not_called()
        get_user_submissions.assert_not_called()
        get_sub_submissions.assert_called()

    @patch(f'{DL}.get_subreddit_submissions')
    @patch(f'{DL}.get_user_submissions')
    @patch(f'{DL}.get_reddit_object_submissions')
    def test_setup_for_ro_download(self, get_ro_submissions, get_user_submissions, get_sub_submissions, reddit_utils):
        download_runner = DownloadRunner(reddit_object_id_list=[2, 3, 4])
        download_runner.run_download()
        get_ro_submissions.assert_called()
        get_user_submissions.assert_not_called()
        get_sub_submissions.assert_not_called()

    @patch(f'{DL}.validate_subreddit_list')
    @patch(f'{DL}.get_subreddit_submissions')
    @patch(f'{DL}.get_user_submissions')
    @patch(f'{DL}.get_reddit_object_submissions')
    def test_setup_for_restricted_download(self, get_ro_submissions, get_user_submissions, get_sub_submissions,
                                           validate_subreddit_list, reddit_utils):
        download_runner = DownloadRunner(user_id_list=[2, 3, 4], subreddit_id_list=[4, 6, 2])
        download_runner.run_download()
        get_ro_submissions.assert_not_called()
        get_user_submissions.assert_called()
        get_sub_submissions.assert_not_called()
        validate_subreddit_list.assert_called()
        self.assertTrue(download_runner.filter_subreddits)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_old_stickied_posts(self, get_raw_submissions, reddit_utils):
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=100), stickied=True))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(20, len(mock_submissions))

        download_runner = DownloadRunner()
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(8, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertFalse(sub.stickied)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_new_stickied_posts(self, get_raw_submissions, reddit_utils):
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x), stickied=True))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(20, len(mock_submissions))

        download_runner = DownloadRunner()
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        stickied = 0
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            if sub.stickied:
                stickied += 1
        self.assertEqual(2, stickied)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_no_stickied_posts(self, get_raw_submissions, reddit_utils):
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(20, len(mock_submissions))

        download_runner = DownloadRunner()
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_old_stickied_posts_restricted_download(self, get_raw_submissions, reddit_utils):
        allowed_subreddit = get_blank_subreddit(name='allowed')
        setattr(allowed_subreddit, 'display_name', 'allowed')
        forbidden_subreddit = get_blank_subreddit(name='forbidden')
        setattr(forbidden_subreddit, 'display_name', 'forbidden')
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=100), stickied=True,
                                                 subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(34, len(mock_submissions))

        download_runner = DownloadRunner()
        download_runner.filter_subreddits = True
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(8, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertFalse(sub.stickied)
            self.assertNotEqual(sub.subreddit, forbidden_subreddit)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_new_stickied_posts_restricted_download(self, get_raw_submissions, reddit_utils):
        allowed_subreddit = get_blank_subreddit(name='allowed')
        setattr(allowed_subreddit, 'display_name', 'allowed')
        forbidden_subreddit = get_blank_subreddit(name='forbidden')
        setattr(forbidden_subreddit, 'display_name', 'forbidden')
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x), stickied=True,
                                                 subreddit=allowed_subreddit))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=allowed_subreddit))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(38, len(mock_submissions))

        download_runner = DownloadRunner()
        download_runner.filter_subreddits = True
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        stickied = 0
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertNotEqual(sub.subreddit, forbidden_subreddit)
            if sub.stickied:
                stickied += 1
        self.assertEqual(2, stickied)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_no_stickied_posts_restricted_download(self, get_raw_submissions, reddit_utils):
        allowed_subreddit = get_blank_subreddit(name='allowed')
        setattr(allowed_subreddit, 'display_name', 'allowed')
        forbidden_subreddit = get_blank_subreddit(name='forbidden')
        setattr(forbidden_subreddit, 'display_name', 'forbidden')
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=allowed_subreddit))
        for x in range(20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(40, len(mock_submissions))

        download_runner = DownloadRunner()
        download_runner.filter_subreddits = True
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertNotEqual(sub.subreddit, forbidden_subreddit)























    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_old_pinned_posts(self, get_raw_submissions, reddit_utils):
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=100), pinned=True))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(20, len(mock_submissions))

        download_runner = DownloadRunner()
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(8, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertFalse(sub.stickied)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_new_pinned_posts(self, get_raw_submissions, reddit_utils):
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x), pinned=True))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(20, len(mock_submissions))

        download_runner = DownloadRunner()
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        pinned = 0
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            if sub.pinned:
                pinned += 1
        self.assertEqual(2, pinned)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_old_pinned_posts_restricted_download(self, get_raw_submissions, reddit_utils):
        allowed_subreddit = get_blank_subreddit(name='allowed')
        setattr(allowed_subreddit, 'display_name', 'allowed')
        forbidden_subreddit = get_blank_subreddit(name='forbidden')
        setattr(forbidden_subreddit, 'display_name', 'forbidden')
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=100), pinned=True,
                                                 subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(34, len(mock_submissions))

        download_runner = DownloadRunner()
        download_runner.filter_subreddits = True
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(8, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertFalse(sub.stickied)
            self.assertNotEqual(sub.subreddit, forbidden_subreddit)

    @patch(f'{DL}.get_raw_submissions')
    def test_get_submissions_with_new_pinned_posts_restricted_download(self, get_raw_submissions, reddit_utils):
        allowed_subreddit = get_blank_subreddit(name='allowed')
        setattr(allowed_subreddit, 'display_name', 'allowed')
        forbidden_subreddit = get_blank_subreddit(name='forbidden')
        setattr(forbidden_subreddit, 'display_name', 'forbidden')
        user = get_blank_user(absolute_date_limit=self.now - timedelta(days=10))
        mock_submissions = []
        for x in range(2):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x), pinned=True,
                                                 subreddit=allowed_subreddit))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=allowed_subreddit))
        for x in range(2, 20):
            mock_submissions.append(MockPrawPost(created=self.now - timedelta(days=x),
                                                 subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_submissions)
        self.assertEqual(38, len(mock_submissions))

        download_runner = DownloadRunner()
        download_runner.filter_subreddits = True
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, user)

        self.assertEqual(10, len(submissions))
        pinned = 0
        for sub in submissions:
            self.assertGreater(sub.created, user.absolute_date_limit.timestamp())
            self.assertNotEqual(sub.subreddit, forbidden_subreddit)
            if sub.pinned:
                pinned += 1
        self.assertEqual(2, pinned)
