from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.core.content_filter import ContentFilter
from DownloaderForReddit.database.database_handler import DatabaseHandler
from DownloaderForReddit.utils import injector
from Tests.mockobjects.mock_objects import (get_user, get_post, get_content, get_mock_reddit_video_post,
                                            get_mock_reddit_uploads_post)


class TestContentFilter(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_settings_manager = MagicMock()
        injector.settings_manager = cls.mock_settings_manager

    def setUp(self):
        self.content_filter = ContentFilter()

    def test_filter_duplicate_url_already_in_db_avoid_duplicates(self):
        db = DatabaseHandler(in_memory=True)
        with db.get_scoped_session() as session:
            content = get_content()
            post = content.post
            session.add(content, post)
            session.commit()

            f = self.content_filter.filter_duplicate(post, content.url)
            self.assertFalse(f)

    def test_filter_duplicate_new_url_avoid_duplicates(self):
        added_url = 'https://www.fakesite.com/323sds9sd9wn3lk23.jpg'
        new_url = 'https://www.realsite.com/2340sdfilnj23lk324kj.png'
        db = DatabaseHandler(in_memory=True)
        with db.get_scoped_session() as session:
            content = get_content(url=added_url)
            post = content.post
            session.add(content, post)
            session.commit()

            f = self.content_filter.filter_duplicate(post, new_url)
            self.assertTrue(f)

    def test_filter_duplicate_url_already_in_db_do_not_avoid_duplicates(self):
        db = DatabaseHandler(in_memory=True)
        with db.get_scoped_session() as session:
            user = get_user(avoid_duplicates=False)
            content = get_content(user=user)
            post = content.post
            session.add(content)
            session.commit()

            self.assertEqual(post.significant_reddit_object, user)
            f = self.content_filter.filter_duplicate(post, content.url)
            self.assertTrue(f)

    def test_filter_reddit_video_allowed_in_settings(self):
        self.mock_settings_manager.download_reddit_hosted_videos = True
        post = get_mock_reddit_video_post()
        f = self.content_filter.filter_reddit_video(post)
        self.assertTrue(f)

    def test_filter_reddit_video_not_allowed_in_settings(self):
        self.mock_settings_manager.download_reddit_hosted_videos = False
        post = get_mock_reddit_video_post()
        f = self.content_filter.filter_reddit_video(post)
        self.assertFalse(f)

    def test_filter_non_reddit_video_not_allowed_in_settings(self):
        self.mock_settings_manager.download_reddit_hosted_videos = False
        post = get_mock_reddit_uploads_post()
        f = self.content_filter.filter_reddit_video(post)
        self.assertTrue(f)

    def test_filter_file_type_image_not_allowed(self):
        user = get_user(download_images=False)
        post = get_post(author=user, significant=user)
        ext = 'jpg'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

    def test_filter_file_type_image_allowed(self):
        user = get_user(download_images=True)
        post = get_post(author=user, significant=user)
        ext = 'jpg'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertTrue(f)

    def test_filter_file_type_gifs_not_allowed(self):
        user = get_user(download_gifs=False)
        post = get_post(author=user, significant=user)
        ext = 'webm'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

    def test_filter_file_type_gifs_allowed(self):
        user = get_user(download_gifs=True)
        post = get_post(author=user, significant=user)
        ext = 'webm'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertTrue(f)

    def test_filter_file_type_videos_not_allowed(self):
        user = get_user(download_videos=False)
        post = get_post(author=user, significant=user)
        ext = 'mp4'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

    def test_filter_file_type_videos_allowed(self):
        user = get_user(download_videos=True)
        post = get_post(author=user, significant=user)
        ext = 'mp4'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertTrue(f)

    def test_filter_file_type_image_cross_contamination(self):
        user = get_user(download_images=False)
        post = get_post(author=user, significant=user)
        ext = 'jpg'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

        self.assertTrue(self.content_filter.filter_file_type(post, 'mp4'))
        self.assertTrue(self.content_filter.filter_file_type(post, 'webm'))

    def test_filter_file_type_gifs_cross_contamination(self):
        user = get_user(download_gifs=False)
        post = get_post(author=user, significant=user)
        ext = 'webm'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

        self.assertTrue(self.content_filter.filter_file_type(post, 'jpg'))
        self.assertTrue(self.content_filter.filter_file_type(post, 'mp4'))

    def test_filter_file_type_video_cross_contamination(self):
        user = get_user(download_videos=False)
        post = get_post(author=user, significant=user)
        ext = 'mp4'
        f = self.content_filter.filter_file_type(post, ext)
        self.assertFalse(f)

        self.assertTrue(self.content_filter.filter_file_type(post, 'jpg'))
        self.assertTrue(self.content_filter.filter_file_type(post, 'webm'))
