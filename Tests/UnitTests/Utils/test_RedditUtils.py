from unittest import TestCase
from unittest.mock import Mock
import logging

from DownloaderForReddit.utils import reddit_utils


class TestRedditUtils(TestCase):

    logging.disable(logging.CRITICAL)

    def setUp(self):
        self.author_name = 'test_author'
        self.sub_name = 'test_subreddit'
        self.url = 'test.url.com/23l4kj'
        self.author = Mock()
        self.author.name = self.author_name
        self.subreddit = Mock()
        self.subreddit.display_name = self.sub_name
        self.title = 'test_title'
        self.created = 86400
        self.domain = 'test.com'
        self.praw_post = Mock(url=self.url, author=self.author, subreddit=self.subreddit, title=self.title,
                              created=self.created, domain=self.domain)

    def test_convert_praw_post_valid_praw_post(self):
        post = reddit_utils.convert_praw_post(self.praw_post)

        self.assertEqual(self.url, post.url)
        self.assertEqual(self.author_name, post.author)
        self.assertEqual(self.sub_name, post.subreddit)
        self.assertEqual(self.title, post.title)
        self.assertEqual(self.created, post.created)
        self.assertEqual(self.domain, post.domain)

    def test_convert_praw_post_invalid_praw_post(self):
        praw_post = TestObject()

        post = reddit_utils.convert_praw_post(praw_post)

        value = 'unknown'
        self.assertEqual(value, post.url)
        self.assertEqual(value, post.author)
        self.assertEqual(value, post.subreddit)
        self.assertEqual(value, post.title)
        self.assertEqual(None, post.domain)
        self.assertEqual('failed to convert post', post.status)

    def test_convert_praw_post_invalid_author_and_subreddit_name(self):
        self.praw_post.author = TestObject()
        self.praw_post.subreddit = TestObject()

        post = reddit_utils.convert_praw_post(self.praw_post)

        self.assertEqual(self.url, post.url)
        self.assertEqual('Unable to find author name', post.author)
        self.assertEqual('Unable to find subreddit name', post.subreddit)
        self.assertEqual(self.title, post.title)
        self.assertEqual(self.created, post.created)
        self.assertEqual(self.domain, post.domain)


class TestObject:

    """
    Valueless object to test methods that should handle attribute errors.
    """

    def __init__(self):
        pass
