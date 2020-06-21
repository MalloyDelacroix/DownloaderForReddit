"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


from time import time
import youtube_dl

from .base_extractor import BaseExtractor
from ..core import const
from ..local_logging import log_utils
from ..utils import injector


class GenericVideoExtractor(BaseExtractor):

    key = None
    load_time = None

    @classmethod
    def get_url_key(cls):
        if cls.load_time is None or cls.load_time < injector.get_settings_manager().supported_videos_updated:
            try:
                with open(const.SUPPORTED_SITES_FILE, 'r') as file:
                    cls.key = [x.strip().strip('*') for x in file.readlines() if x.endswith('*\n')]
                    load_time = time()
                    cls.load_time = load_time
                    injector.get_settings_manager().supported_videos_updated = load_time
            except FileNotFoundError:
                cls.key = None
                log_utils.log_proxy(__name__, 'WARNING', message='Failed to load supported video sites')
        return cls.key

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)

    def extract_content(self):
        try:
            # TODO: need way to kill this when session is terminated
            with youtube_dl.YoutubeDL({'format': 'mp4'}) as ydl:
                result = ydl.extract_info(self.url, download=False)
            if 'entries' in result:
                self.extract_playlist(result['entries'])
            else:
                self.extract_single_video(result)
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message, failed_domain=self.post.domain)

    def extract_single_video(self, entry):
        self.make_content(entry['url'], 'mp4')

    def extract_playlist(self, playlist):
        count = 1
        for entry in playlist:
            self.make_content(entry['url'], 'mp4', count=count)
            count += 1
