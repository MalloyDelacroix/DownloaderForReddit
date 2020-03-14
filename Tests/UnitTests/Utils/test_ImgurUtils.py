import unittest
from unittest.mock import patch, MagicMock
import json
from os import path

from DownloaderForReddit.Utils import Injector, ImgurUtils
from DownloaderForReddit.Utils.ImgurUtils import ImgurError
from DownloaderForReddit.Core import Const
from Tests.MockObjects.MockSettingsManager import MockSettingsManager



class TestImgurUtils(unittest.TestCase):

    def setUp(self):
        Injector.settings_manager = MockSettingsManager()

    @patch('requests.get')
    def test_check_credits(self, req_mock: MagicMock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _get_json_from_file(r"Resources\credit_resp.txt")

        req_mock.return_value = mock_response

        value = ImgurUtils.check_credits()

        url = 'https://api.imgur.com/3/credits'
        header = {
            'Authorization': 'Client-ID {{CLIENT ID}}'
        }
        req_mock.assert_called_with(url, headers=header)
        self.assertEqual(497, value)
        self.assertEqual(497, ImgurUtils.num_credits)
        self.assertEqual(1584168402, ImgurUtils.credit_reset_time)
        pass

    def test_get_link_gif(self):
        link = ImgurUtils.get_link(_get_json_from_file(r'Resources\gif_res.txt')['data'])
        self.assertEqual('https://i.imgur.com/mOlfhY3.mp4', link)


def _get_json_from_file(file_name):
    current_folder_path = path.dirname(path.abspath(__file__))
    with open(path.join(current_folder_path, file_name)) as file:
        return json.loads(file.read())

