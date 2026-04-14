from unittest.mock import MagicMock

from DownloaderForReddit.extractors import RedditUploadsExtractor
from Tests.unittests.extractors.abstract_extractor_test import ExtractorTest


class TestRedditUploadsExtractor(ExtractorTest):

    def test_get_album_item_url_image(self):
        test_url = 'https://preview.redd.it/w8k58f0hqstg1.jpg?width=640&format=pjpg&auto=webp&s=d21d6608b544946186602108e501ef096f614d80'
        container_data = {
            "y": 627,
            "x": 640,
            "u": test_url,
        }

        extractor = RedditUploadsExtractor(MagicMock())
        url = extractor.get_album_item_url(container_data)
        self.assertEqual(url, test_url)

    def test_get_album_item_url_gif(self):
        container_data = {
            "y": 640,
            "gif": "https://i.redd.it/6lqj0jhjqstg1.gif",
            "mp4": "https://preview.redd.it/6lqj0jhjqstg1.gif?format=mp4&s=bd89b21b1a23f340cebb629a440517fd2226dd64",
            "x": 360
        }

        extractor = RedditUploadsExtractor(MagicMock())
        url = extractor.get_album_item_url(container_data)
        self.assertEqual(url, 'https://preview.redd.it/6lqj0jhjqstg1.gif?format=mp4&s=bd89b21b1a23f340cebb629a440517fd2226dd64')

    def test_get_media_extension_image(self):
        test_url = 'https://preview.redd.it/w8k58f0hqstg1.jpg?width=640&format=pjpg&auto=webp&s=d21d6608b544946186602108e501ef096f614d80'

        extractor = RedditUploadsExtractor(MagicMock())
        ext = extractor.get_media_extension(test_url)
        self.assertEqual(ext, 'jpg')

    def test_get_media_extension_gif(self):
        test_url = 'https://preview.redd.it/6lqj0jhjqstg1.gif?format=mp4&s=bd89b21b1a23f340cebb629a440517fd2226dd64'

        extractor = RedditUploadsExtractor(MagicMock())
        ext = extractor.get_media_extension(test_url)
        self.assertEqual(ext, 'mp4')

    def test_get_media_extension_mp4(self):
        test_url = 'https://i.redd.it/6lqj0jhjqstg1.mp4#format=mp4&s=asd90fu0j234inmosdif0s9ufoi324joisdfkjllksd'

        extractor = RedditUploadsExtractor(MagicMock())
        ext = extractor.get_media_extension(test_url)
        self.assertEqual(ext, 'mp4')
