from unittest.mock import patch

from .abstract_extractor_test import ExtractorTest
from DownloaderForReddit.extractors.direct_extractor import DirectExtractor
from Tests.mockobjects.MockObjects import get_post


class TestDirectExtractor(ExtractorTest):

    PATH = 'DownloaderForReddit.extractors.direct_extractor.DirectExtractor'

    @patch(f'{PATH}.make_dir_path')
    @patch(f'{PATH}.make_title')
    @patch(f'{PATH}.check_duplicate_content')
    def test_extract_direct_link(self, check_duplicate, make_title, make_dir_path):
        url = 'https://unsupported_site.com/image/3jfd9nlksd.jpg'
        post = get_post(url=url)
        self.session.add(post)

        check_duplicate.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        de = DirectExtractor(post)
        de.extract_content()

        content = de.extracted_content[0]
        self.assertEqual(url, content.url)
        self.assertEqual(post.title, content.title)
        self.assertEqual(post.author, content.user)
        self.assertEqual(post.subreddit, content.subreddit)
        self.assertEqual(post, content.post)
        self.assertIsNotNone(content.id)
