import unittest
from unittest.mock import patch

from DownloaderForReddit.extractors.reddit_video_extractor import RedditVideoExtractor
from DownloaderForReddit.utils import injector
from DownloaderForReddit.utils import video_merger
from Tests.MockObjects.MockSettingsManager import MockSettingsManager
from Tests.MockObjects import MockObjects


class TestRedditVideoExtractor(unittest.TestCase):

    def setUp(self):
        injector.settings_manager = MockSettingsManager()
        video_merger.videos_to_merge.clear()

    def test_extract_gif(self):
        post = MockObjects.get_mock_post_reddit_video()
        fallback_url = post.url + '/DASH_2_4_M?source=fallback'
        post.media = {'reddit_video': {'fallback_url': fallback_url}}

        re = RedditVideoExtractor(post, MockObjects.get_user())
        re.extract_content()

        self.assertEqual(1, len(re.extracted_content))
        content = re.extracted_content[0]
        self.assertEqual(fallback_url, content.url)
        self.assertEqual('PublicFreakout', content.subreddit)
        self.assertEqual('Reddit Video Broh', content.post_title)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde.mp4', content.make_filename())

        self.assertEqual(0, len(re.failed_extract_posts))
        self.assertEqual(0, len(video_merger.videos_to_merge))

    def test_extract_video_with_audio(self):
        post = MockObjects.get_mock_post_reddit_video()
        post.is_video = True
        fallback_url = post.url + '/DASH_2_4_M?source=fallback'
        post.media = {'reddit_video': {'fallback_url': fallback_url}}

        re = RedditVideoExtractor(post, MockObjects.get_user())
        re.extract_content()

        self.assertEqual(2, len(re.extracted_content))

        vid_content = re.extracted_content[0]
        self.assertEqual(fallback_url, vid_content.url)
        self.assertEqual('PublicFreakout', vid_content.subreddit)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde(video).mp4', vid_content.make_filename())

        audio_content = re.extracted_content[1]
        self.assertEqual(post.url + '/audio', audio_content.url)
        self.assertEqual('PublicFreakout', audio_content.subreddit)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde(audio).mp3', audio_content.make_filename())

        self.assertEqual(0, len(re.failed_extract_posts))
        self.assertEqual(1, len(video_merger.videos_to_merge))

    @patch('DownloaderForReddit.Extractors.RedditVideoExtractor.get_host_vid')
    def test_extract_video_with_audio_crossposted_post(self, rv_mock):
        parent_post = MockObjects.get_mock_post_reddit_video()
        parent_id = 'pppppp'
        parent_post.id = parent_id
        parent_post.is_video = True
        parent_post.title = 'Whoa, Parent Vid'
        parent_post.subreddit = 'DefinitelyNotPublicFreakout'
        fallback_url = parent_post.url + '/DASH_2_4_M?source=fallback'
        parent_post.media = {'reddit_video': {'fallback_url': fallback_url}}
        rv_mock.return_value = parent_post

        post = MockObjects.get_mock_post_reddit_video()
        post.crosspost_parent = 'notsurewhatgoeshere_' + parent_id
        post.url = 'https://v.redd.it/nottherealurl'

        re = RedditVideoExtractor(post, MockObjects.get_user())
        re.extract_content()

        rv_mock.assert_called()

        self.assertEqual(2, (len(re.extracted_content)))

        vid_content = re.extracted_content[0]
        self.assertEqual(fallback_url, vid_content.url)
        self.assertEqual('PublicFreakout', vid_content.subreddit)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde(video).mp4', vid_content.make_filename())

        audio_content = re.extracted_content[1]
        self.assertEqual(parent_post.url + '/audio', audio_content.url)
        self.assertEqual('PublicFreakout', audio_content.subreddit)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde(audio).mp3', audio_content.make_filename())

        self.assertEqual(0, len(re.failed_extract_posts))
        self.assertEqual(1, len(video_merger.videos_to_merge))

    @patch('DownloaderForReddit.Extractors.RedditVideoExtractor.get_audio_content')
    def test_extract_video_with_audio_extract_exception(self, rv_mock):
        rv_mock.side_effect = AttributeError
        post = MockObjects.get_mock_post_reddit_video()
        post.is_video = True
        fallback_url = post.url + '/DASH_2_4_M?source=fallback'
        post.media = {'reddit_video': {'fallback_url': fallback_url}}

        re = RedditVideoExtractor(post, MockObjects.get_user())
        re.extract_content()

        self.assertEqual(1, len(re.extracted_content))

        vid_content = re.extracted_content[0]
        self.assertEqual(fallback_url, vid_content.url)
        self.assertEqual('PublicFreakout', vid_content.subreddit)
        self.assertEqual('C:/Users/Gorgoth/Downloads/JohnEveryman/abcde(video).mp4', vid_content.make_filename())

        self.assertEqual(1, len(re.failed_extract_posts))
        self.assertEqual(0, len(video_merger.videos_to_merge))

    @patch('DownloaderForReddit.Extractors.RedditVideoExtractor.get_vid_url')
    def test_extract_video_failed_to_find_url(self, rv_mock):
        rv_mock.return_value = None
        post = MockObjects.get_mock_post_reddit_video()
        post.is_video = True

        re = RedditVideoExtractor(post, MockObjects.get_user())
        re.extract_content()

        self.assertEqual(1, len(re.failed_extract_posts))
        self.assertEqual(0, len(re.extracted_content))
