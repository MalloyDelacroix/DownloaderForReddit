from datetime import datetime
from unittest import TestCase

from DownloaderForReddit.database.database_handler import DatabaseHandler
from DownloaderForReddit.database.models import (RedditObjectList, RedditObject, User, Subreddit, Post, Comment,
                                                 Content, DownloadSession)


class TestRedditObjectFilter(TestCase):

    def setUp(self) -> None:
        self.db = DatabaseHandler(in_memory=True)
        with self.db.get_scoped_session() as session:
            for ro in ['ro_one', 'ro_two', 'ro_three', 'ro_four', 'ro_five']:
                session.add(User(name=ro.replace('ro', 'user')))
                session.add(Subreddit(name=ro.replace('ro', 'subreddit')))
            for x in range(20):
                post = Post(title=f'Test Post', score=10000, date_posted=datetime(year=2019, month=6, day=4),
                            domain='fakesite.com', reddit_id=f'id-{x}', url='fakesite.com/234dfwsu09', )
