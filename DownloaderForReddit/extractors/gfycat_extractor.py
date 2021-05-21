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

from os import path
from urllib.parse import urlparse

import requests

from .base_extractor import BaseExtractor
from ..core.errors import Error
from ..core import const

_REDGIFS_ENDPOINT = "https://api.redgifs.com/v1/gfycats/"
_GFYCAT_ENDPOINT = "https://api.gfycat.com/v1/gfycats/"


class GfycatExtractor(BaseExtractor):

    url_key = ['gfycat', 'redgifs']

    def __init__(self, post, **kwargs):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the gfycat website through their
        api.
        """
        super().__init__(post, **kwargs)
        item = urlparse(self.url)
        if 'redgifs' in item.hostname:
            self.api_caller = "https://api.redgifs.com/v1/gfycats/"
        else:
            self.api_caller = "https://api.gfycat.com/v1/gfycats/"

    def extract_content(self):
        """Dictates which extraction method should be used"""
        try:
            if self.url.lower().endswith(const.GIF_EXT) or self.url.lower().endswith(const.VID_EXT):
                self.extract_direct_link()
            else:
                self.extract_single()
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message)

    def extract_single(self):
        item = urlparse(self.url)
        gif_id = item.path
        if gif_id.startswith("/watch/"):
            gif_id = gif_id[len('/watch/'):]
        gif_id = path.basename(gif_id).split('-')[0]

        if 'redgifs' in item.hostname:
            gfy_json = self.get_json(_REDGIFS_ENDPOINT + gif_id)
        else:
            response = requests.get(_GFYCAT_ENDPOINT + gif_id, timeout=10)
            if response.status_code == 200 and 'json' in response.headers['Content-Type']:
                gfy_json = response.json()
            else:
                gfy_json = self.get_json(_REDGIFS_ENDPOINT + gif_id.lower())  # refgif ids are all lowercase

        # First we attempt to extract the preferred mp4 url, if that is not successful we try the webm url.  If neither
        # are available, the error is handled.
        gfy_url = gfy_json.get('gfyItem').get('mp4Url')
        if gfy_url is not None:
            self.make_content(gfy_url, 'mp4', media_id=gif_id)
            return
        gfy_url = gfy_json.get('gfyItem').get('webmUrl')
        if gfy_url is None:
            message = 'Failed to locate an appropriate download url within the response json'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extraction_error_message=message)
        else:
            self.make_content(gfy_url, 'webm', media_id=gif_id)
