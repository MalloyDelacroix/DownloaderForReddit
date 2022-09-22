from unittest.mock import patch, MagicMock

from .abstract_extractor_test import ExtractorTest
from Tests.mockobjects import mock_objects
from DownloaderForReddit.extractors.redgifs_extractor import RedgifsExtractor


@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_dir_path')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.make_title')
@patch('DownloaderForReddit.extractors.base_extractor.BaseExtractor.filter_content')
class TestRedgifsExtractor(ExtractorTest):

    @patch('DownloaderForReddit.extractors.redgifs_extractor.RedgifsExtractor.get_json')
    def test_redgifs_single_extraction(self, get_json, filter_content, make_title, make_dir_path):
        filter_content.return_value = True
        post = mock_objects.get_mock_post_gfycat(session=self.session)
        post.url = 'https://www.redgifs.com/watch/decisivecleanfallowdeer'
        expected_output = 'https://thumbs4.redgifs.com/subparmauveevisceratingkracken.mp4?expires=1663866000&signature=670633f059f90e83cc10cf8aea5518ae77f202b312ea5ab9ef8563b4c560f652&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b'

        get_json.return_value = {
          "gif": {
            "id": "subparmauveevisceratingkracken",
            "createDate": 1663770890,
            "hasAudio": "true",
            "width": 1920,
            "height": 1080,
            "likes": 22657,
            "tags": [],
            "verified": "false",
            "views": "null",
            "duration": 51.433,
            "published": "true",
            "urls": {
              "vthumbnail": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.mp4?expires=1663866000&signature=81e59342b722ea7c63fa9f566616fd7d1f7607adadcb928d532fb3b5d2c84ef7&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
              "thumbnail": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.jpg?expires=1663866000&signature=f65b0ea25ac3c3798430b22c97912c662d5d968d2ea415ae9afa2f8eba12f84b&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
              "sd": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.mp4?expires=1663866000&signature=81e59342b722ea7c63fa9f566616fd7d1f7607adadcb928d532fb3b5d2c84ef7&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
              "hd": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken.mp4?expires=1663866000&signature=670633f059f90e83cc10cf8aea5518ae77f202b312ea5ab9ef8563b4c560f652&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
              "poster": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-poster.jpg?expires=1663866000&signature=a7962fec746ef4ccae9b9c110c1e6aea9300c4330907aae76a55809ddd856c19&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b"
            },
            "type": 1,
            "avgColor": "#000000",
            "gallery": "null",
            "hideHome": "false",
            "hideTrending": "false"
          },
          "user": "null"
        }

        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ex = RedgifsExtractor(post)
        ex.extract_content()
        self.check_output(ex, expected_output, post)

    @patch('DownloaderForReddit.extractors.redgifs_extractor.RedgifsExtractor.get_json')
    def test_redgifs_non_hd_fallback_url(self, get_json, filter_content, make_title, make_dir_path):
        filter_content.return_value = True
        post = mock_objects.get_mock_post_gfycat(session=self.session)
        post.url = 'https://www.redgifs.com/watch/subparmauveevisceratingkracken'
        expected_output = 'https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.mp4?expires=1663866000&signature=81e59342b722ea7c63fa9f566616fd7d1f7607adadcb928d532fb3b5d2c84ef7&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b'

        get_json.return_value = {
            "gif": {
                "id": "subparmauveevisceratingkracken",
                "createDate": 1663770890,
                "hasAudio": "true",
                "width": 1920,
                "height": 1080,
                "likes": 22657,
                "tags": [],
                "verified": "false",
                "views": "null",
                "duration": 51.433,
                "published": "true",
                "urls": {
                    "vthumbnail": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.mp4?expires=1663866000&signature=81e59342b722ea7c63fa9f566616fd7d1f7607adadcb928d532fb3b5d2c84ef7&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
                    "thumbnail": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.jpg?expires=1663866000&signature=f65b0ea25ac3c3798430b22c97912c662d5d968d2ea415ae9afa2f8eba12f84b&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
                    "sd": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-mobile.mp4?expires=1663866000&signature=81e59342b722ea7c63fa9f566616fd7d1f7607adadcb928d532fb3b5d2c84ef7&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b",
                    "poster": "https://thumbs4.redgifs.com/subparmauveevisceratingkracken-poster.jpg?expires=1663866000&signature=a7962fec746ef4ccae9b9c110c1e6aea9300c4330907aae76a55809ddd856c19&for=2603:6011:5b03:6a00:8dfa:6499:fe39:8c0b"
                },
                "type": 1,
                "avgColor": "#000000",
                "gallery": "null",
                "hideHome": "false",
                "hideTrending": "false"
            },
            "user": "null"
        }

        make_title.return_value = post.title
        make_dir_path.return_value = 'content_dir_path'

        ex = RedgifsExtractor(post)
        ex.extract_content()
        self.check_output(ex, expected_output, post)

    @patch('DownloaderForReddit.extractors.redgifs_extractor.RedgifsExtractor.extract_single')
    def test_failed_connection(self, es_mock, filter_content, make_title, make_dir_path):
        es_mock.side_effect = ConnectionError()
        post = mock_objects.get_mock_redgifs()

        ge = RedgifsExtractor(post)
        ge.extract_content()

        self.assertTrue(ge.failed_extraction)
        self.assertIsNotNone(ge.failed_extraction_message)
