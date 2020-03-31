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


import youtube_dl

from ..Extractors.BaseExtractor import BaseExtractor
from ..Core import Const
from ..Logging import LogUtils


class GenericVideoExtractor(BaseExtractor):

    try:
        file = open(Const.SUPPORTED_SITES_FILE, 'r')
        url_key = [x.strip() for x in file.readlines()]
        file.close()
    except FileNotFoundError:
        url_key = None
        LogUtils.log_proxy(__name__, 'WARNING', message='Failed to load supported video sites')

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)

    def extract_content(self):
        try:
            with youtube_dl.YoutubeDL({'format': 'mp4'}) as ydl:
                result = ydl.extract_info(self.url, download=False)
            if 'entries' in result:
                self.extract_playlist(result['entries'])
            else:
                self.extract_single_video(result)
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message, failed_domain=self.domain)

    def extract_single_video(self, entry):
        self.make_content(entry['url'], self.get_filename(entry['id']), 'mp4')

    def extract_playlist(self, playlist):
        count = 1
        for entry in playlist:
            self.make_content(entry['url'], self.get_filename(entry['id']), 'mp4', count=count)
            count += 1
