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


from ..Extractors.BaseExtractor import BaseExtractor
from ..Core import Const

from urllib.parse import urlparse
import requests

_REDGIFS_ENDPOINT = "https://api.redgifs.com/v1/gfycats"
_GFYCAT_ENDPOINT = "https://api.gfycat.com/v1/gfycats"

class GfycatExtractor(BaseExtractor):

    url_key = ['gfycat','redgifs']

    def __init__(self, post, reddit_object, content_display_only=False):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the gfycat website through their
        api
        """
        super().__init__(post, reddit_object, content_display_only)


    def extract_content(self):
        """Dictates which extraction method should be used"""
        try:
            if self.url.lower().endswith(Const.GIF_EXT):
                self.extract_direct_link()
            else:
                self.extract_single()
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message)

    def extract_single(self):
        item = urlparse(self.url)
        gif_id = item.path.split('-', 1)[0]
        print(gif_id)

        if item.hostname == 'redgifs.com':
            gfy_json = self.get_json(_REDGIFS_ENDPOINT + gif_id)
        else:
            response = requests.get(_GFYCAT_ENDPOINT + gif_id)
            if response.status_code == 200 and 'json' in response.headers['Content-Type']:
                gfy_json = response.json()
            else:
                gfy_json = self.get_json(_REDGIFS_ENDPOINT + gif_id)

        gfy_url = gfy_json.get('gfyItem').get('webmUrl')
        file_name = self.get_filename(gif_id[1:])
        self.make_content(gfy_url, file_name, 'webm')
