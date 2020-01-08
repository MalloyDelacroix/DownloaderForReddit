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

from bs4 import BeautifulSoup

from ..Extractors.BaseExtractor import BaseExtractor
from ..Core import Const


class VidbleExtractor(BaseExtractor):
    url_key = ['vidble']

    def __init__(self, post, reddit_object, content_display_only=False):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the Vidble website via
        BeautifulSoup4.
        """
        super().__init__(post, reddit_object, content_display_only)
        self.vidble_base = "https://vidble.com"

    def extract_content(self):
        try:
            if '/album/' in self.url:
                self.extract_album()
            else:
                # We can convert show and explore links to single links by removing the show/explore from the url
                self.url = self.url.replace('/show/', '/').replace('/explore/', '/')
                if self.url.lower().endswith(Const.ALL_EXT):
                    self.extract_direct_link()
                else:
                    self.extract_single()
        except Exception:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message)

    def get_imgs(self):
        soup = BeautifulSoup(self.get_text(self.url), 'html.parser')
        return soup.find_all('img')

    def extract_single(self):
        domain, vidble_id = self.url.rsplit('/', 1)
        # There should only be one image
        img = self.get_imgs()[0]
        # We only need to get the filename from the image
        link = img.get('src')
        if link is not None:
            base, extension = link.rsplit('.', 1)
            file_name = "{}.{}".format(vidble_id, extension)
            url = self.vidble_base + '/' + file_name
            self.make_content(url, vidble_id, extension)

    def extract_album(self):
        # We will use the undocumented API specified here:
        # https://www.reddit.com/r/Enhancement/comments/29nik6/feature_request_inline_image_expandos_for_vidible/cinha50/
        json = self.get_json(self.url + "?json=1")
        pics = json['pics']
        for raw_pic in pics:
            domain, file_name = raw_pic.rsplit('/', 1)
            file_name = file_name.replace('_med', '')
            base, extension = file_name.rsplit('.', 1)
            url = "https{}/{}".format(domain, file_name)
            self.make_content(url, base, extension)
