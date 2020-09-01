from unittest.mock import patch

from .abstract_extractor_test import ExtractorTest
from Tests.mockobjects.mock_objects import get_post, get_mock_reddit_video_submission
from DownloaderForReddit.extractors.reddit_video_extractor import RedditVideoExtractor
from DownloaderForReddit.utils import video_merger


@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_dir_path')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_title')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.filter_content')
class TestRedditVideoExtractor(ExtractorTest):

    PATH = 'DownloaderForReddit.extractors.RedditVideoExtractor'

    def setUp(self):
        super().setUp()
        video_merger.videos_to_merge.clear()
        self.settings.download_reddit_hosted_videos = True

    @patch(f'{PATH}.get_host_vid')
    def test_extract_gif(self, get_host_vid, filter_content, make_title, make_dir_path):
        url = 'https://v.redd.it/lkfmw864od1971'
        fallback_url = url + '/DASH_2_4_M?source=fallback'
        submission = get_mock_reddit_video_submission(media={'reddit_video': {'fallback_url': fallback_url}})
        get_host_vid.return_value = submission
        post = get_post(url=url, session=self.session, reddit_id=submission.id)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        re = RedditVideoExtractor(post)
        re.extract_content()

        self.check_output(re, fallback_url, post, title=f'{post.title}(video)')

    @patch(f'{PATH}.get_host_vid')
    def test_extract_video_with_audio(self, get_host_vid, filter_content, make_title, make_dir_path):
        url = 'https://v.redd.it/lkfmw864od1971'
        fallback_url = url + '/DASH_2_4_M?source=fallback'
        submission = get_mock_reddit_video_submission(media={'reddit_video': {'fallback_url': fallback_url}},
                                                      is_video=True)
        get_host_vid.return_value = submission
        post = get_post(url=url, session=self.session, reddit_id=submission.id)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        re = RedditVideoExtractor(post)
        re.extract_content()

        self.assertEqual(2, len(re.extracted_content))
        vid_content = re.extracted_content[0]
        self.check(vid_content, fallback_url, post, title=f'{post.title}(video)')
        audio_content = re.extracted_content[1]
        self.check(audio_content, f'{url}/audio', post, title=f'{post.title}(audio)')
        self.assertEqual(1, len(video_merger.videos_to_merge))

    @patch(f'{PATH}.get_host_vid')
    def test_extract_video_with_audio_crossposted_post(self, rv_mock, filter_content, make_title, make_dir_path):
        url = 'https://v.redd.it/lkfmw864od1971'
        fallback_url = url + '/DASH_2_4_M?source=fallback'
        parent_submission = get_mock_reddit_video_submission(
            _id='pppppp',
            is_video=True,
            title='A parent vid',
            subreddit='DefinitelyNotPublicFreakout',
            media={'reddit_video': {'fallback_url': fallback_url}}
        )
        rv_mock.return_value = parent_submission

        submission = get_mock_reddit_video_submission(crosspost_parent=parent_submission,
                                                      url='https://v.redd.it/nottherealurl')
        post = get_post(url=url, session=self.session, reddit_id=submission.id, title=submission.title)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        re = RedditVideoExtractor(post)
        re.extract_content()

        rv_mock.assert_called()

        self.assertEqual(2, (len(re.extracted_content)))
        vid_content = re.extracted_content[0]
        self.check(vid_content, fallback_url, post, title=f'{post.title}(video)')
        audio_content = re.extracted_content[1]
        self.check(audio_content, f'{url}/audio', post, title=f'{post.title}(audio)')
        self.assertEqual(1, len(video_merger.videos_to_merge))

    @patch(f'{PATH}.get_audio_content')
    @patch(f'{PATH}.get_host_vid')
    def test_extract_video_with_audio_extract_exception(self, get_host_vid, get_audio, filter_content, make_title,
                                                        make_dir_path):
        url = 'https://v.redd.it/lkfmw864od1971'
        fallback_url = url + '/DASH_2_4_M?source=fallback'
        get_audio.side_effect = AttributeError
        submission = get_mock_reddit_video_submission(is_video=True,
                                                      media={'reddit_video': {'fallback_url': fallback_url}})
        get_host_vid.return_value = submission
        post = get_post(url=url, session=self.session, reddit_id=submission.id, title=submission.title)
        filter_content.return_value = True
        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        re = RedditVideoExtractor(post)
        re.extract_content()

        self.assertEqual(1, len(re.extracted_content))
        self.check_output(re, fallback_url, post, title=f'{post.title}(video)')
        self.assertEqual(0, len(video_merger.videos_to_merge))

    @patch(f'{PATH}.get_host_vid')
    @patch(f'{PATH}.get_vid_url')
    def test_extract_video_failed_to_find_url(self, get_vid_url, get_host_vid, filter_content, make_title,
                                              make_dir_path):
        submission = get_mock_reddit_video_submission(is_video=True)
        get_vid_url.return_value = None
        get_host_vid.return_value = submission
        post = get_post(title=submission.title, session=self.session)

        re = RedditVideoExtractor(post)
        re.extract_content()

        self.assertEqual(0, len(re.extracted_content))
        self.assertTrue(re.failed_extraction)
        self.assertIsNotNone(re.failed_extraction_message)
