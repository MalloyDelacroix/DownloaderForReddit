from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from DownloaderForReddit.core.download_runner import DownloadRunner
from DownloaderForReddit.utils import injector, reddit_utils
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects.MockObjects import MockPrawPost, MockPrawSubreddit, get_blank_user


class TestDownloadRunner(TestCase):

    def setUp(self):
        injector.settings_manager = MockSettingsManager()
        reddit_utils.reddit_instance = None

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_old_stickied_posts(self, start_extractor, start_downloader, get_raw_submissions):
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=10)
        mock_posts_list = []
        for x in range(2):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=100), stickied=True))
        for x in range(2, 20):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(20, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        submissions = download_runner.get_submissions(None, reddit_user)

        self.assertEqual(8, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)
            self.assertFalse(sub.stickied)

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_new_stickied_posts(self, start_extractor, start_downloader, get_raw_submissions):
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=10)
        mock_posts_list = []
        for x in range(2):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x), stickied=True))
        for x in range(2, 20):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(20, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        submissions = download_runner.get_submissions(None, reddit_user)

        self.assertEqual(10, len(submissions))
        stickied = 0
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)
            if sub.stickied:
                stickied += 1
        self.assertEqual(2, stickied)

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_no_stickied_posts(self, start_extractor, start_downloader, get_raw_submissions):
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=10)
        mock_posts_list = []
        for x in range(20):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x)))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(20, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        submissions = download_runner.get_submissions(None, reddit_user)

        self.assertEqual(10, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_old_stickied_posts_subreddits_filtered(self, start_extractor, start_downloader,
                                                                         get_raw_submissions):
        allowed_subreddit = MockPrawSubreddit(name='allowed')
        forbidden_subreddit = MockPrawSubreddit(name='forbidden')
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=20)
        mock_posts_list = []
        for x in range(2):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=100), stickied=True,
                                                subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=allowed_subreddit))
        for x in range(18, 30):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(30, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, reddit_user, subreddit_filter=True)

        self.assertEqual(16, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)
            self.assertFalse(sub.stickied)

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_new_stickied_posts_subreddits_filtered(self, start_extractor, start_downloader,
                                                                         get_raw_submissions):
        allowed_subreddit = MockPrawSubreddit(name='allowed')
        forbidden_subreddit = MockPrawSubreddit(name='forbidden')
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=20)
        mock_posts_list = []
        for x in range(2):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x), stickied=True,
                                                subreddit=allowed_subreddit))
        for x in range(2, 18):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=allowed_subreddit))
        for x in range(18, 30):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(30, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, reddit_user, subreddit_filter=True)

        self.assertEqual(18, len(submissions))
        stickied = 0
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)
            if sub.stickied:
                stickied += 1
        self.assertEqual(2, stickied)

    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.get_raw_submissions')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_downloader')
    @patch('DownloaderForReddit.core.DownloadRunner.DownloadRunner.start_extractor')
    def test_get_submissions_with_old_stickied_posts_subreddits_filtered(self, start_extractor, start_downloader,
                                                                         get_raw_submissions):
        allowed_subreddit = MockPrawSubreddit(name='allowed')
        forbidden_subreddit = MockPrawSubreddit(name='forbidden')
        reddit_user = get_blank_user()
        reddit_user.date_limit = datetime.now() - timedelta(days=20)
        mock_posts_list = []
        for x in range(18):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=allowed_subreddit))
        for x in range(18, 30):
            mock_posts_list.append(MockPrawPost(created=datetime.now() - timedelta(days=x),
                                                subreddit=forbidden_subreddit))
        get_raw_submissions.return_value = self.submission_generator(mock_posts_list)
        self.assertEqual(30, len(mock_posts_list))

        download_runner = DownloadRunner(None, None, None, None)
        download_runner.validated_subreddits.append(allowed_subreddit.display_name)
        submissions = download_runner.get_submissions(None, reddit_user, subreddit_filter=True)

        self.assertEqual(18, len(submissions))
        for sub in submissions:
            self.assertGreater(sub.created, reddit_user.date_limit)

    def submission_generator(self, post_list):
        for post in post_list:
            yield post
