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


from . import BaseExtractor
from ..Core import Const


class GfycatExtractor(BaseExtractor):

    url_key = ['gfycat', 'redgifs']

    def __init__(self, post, **kwargs):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the gfycat website through their
        api.
        """
        super().__init__(post, **kwargs)
        self.api_caller = "https://api.gfycat.com/v1/gfycats/"

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
        domain, gif_id = self.url.rsplit('/', 1)
        gif_id = gif_id.split('-',1)[0]
        gfy_json = self.get_json(self.api_caller + gif_id)
        gfy_url = gfy_json.get('gfyItem').get('webmUrl')
        self.make_content(gfy_url, 'webm')
