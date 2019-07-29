import unittest

from DownloaderForReddit.Core.PostFilter import PostFilter
from DownloaderForReddit.Utils import Injector
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects.MockObjects import MockPrawPost
from Tests.MockObjects import MockObjects


MOCK_DATE_LIMIT = 1500000000


class MyTestCase(unittest.TestCase):

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()

    def test_score_filter_no_limit_restriction(self):
        Injector.get_settings_manager().restrict_by_score = False
        post_filter = PostFilter()
        post = MockPrawPost(score=10000)
        self.assertTrue(post_filter.score_filter(post))

    def test_score_filter_greater_than_score(self):
        Injector.get_settings_manager().restrict_by_score = True
        post_filter = PostFilter()
        post = MockPrawPost(score=5000)
        self.assertTrue(post_filter.score_filter(post))
        post = MockPrawPost(score=2000)
        self.assertFalse(post_filter.score_filter(post))

    def test_score_filter_less_than_score(self):
        settings_manager = Injector.get_settings_manager()
        settings_manager.restrict_by_score = True
        settings_manager.score_limit_operator = 'LESS'
        post_filter = PostFilter()
        post = MockPrawPost(score=1000)
        self.assertTrue(post_filter.score_filter(post))
        post = MockPrawPost(score=4000)
        self.assertFalse(post_filter.score_filter(post))

    def test_nsfw_filter_include(self):
        post_filter = PostFilter()
        user = MockObjects.get_blank_user()
        post = MockPrawPost(over_18=True)
        self.assertTrue(post_filter.nsfw_filter(post, user))
        post = MockPrawPost(over_18=False)
        self.assertTrue(post_filter.nsfw_filter(post, user))

    def test_nsfw_filter_exclude(self):
        post_filter = PostFilter()
        user = MockObjects.get_blank_user()
        user.nsfw_filter = 'EXCLUDE'
        post = MockPrawPost(over_18=True)
        self.assertFalse(post_filter.nsfw_filter(post, user))
        post = MockPrawPost(over_18=False)
        self.assertTrue(post_filter.nsfw_filter(post, user))

    def test_nsfw_filter_include_only(self):
        post_filter = PostFilter()
        user = MockObjects.get_blank_user()
        user.nsfw_filter = 'ONLY'
        post = MockPrawPost(over_18=True)
        self.assertTrue(post_filter.nsfw_filter(post, user))
        post = MockPrawPost(over_18=False)
        self.assertFalse(post_filter.nsfw_filter(post, user))

    def test_date_limit_last_download_time(self):
        post_filter = PostFilter()
        user = MockObjects.get_blank_user()
        user.date_limit = MOCK_DATE_LIMIT
        post = MockPrawPost(created=MOCK_DATE_LIMIT + 1000)
        self.assertTrue(post_filter.date_filter(post, user))
        post = MockPrawPost(created=MOCK_DATE_LIMIT - 1000)
        self.assertFalse(post_filter.date_filter(post, user))

    def test_date_limit_custom_date_limit(self):
        post_filter = PostFilter()
        user = MockObjects.get_blank_user()
        user.date_limit = 100000
        user.custom_date_limit = MOCK_DATE_LIMIT
        post = MockPrawPost(created=MOCK_DATE_LIMIT + 1000)
        self.assertTrue(post_filter.date_filter(post, user))
        post = MockPrawPost(created=MOCK_DATE_LIMIT - 1000)
        self.assertFalse(post_filter.date_filter(post, user))
