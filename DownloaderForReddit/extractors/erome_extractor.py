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

from .base_extractor import BaseExtractor
from ..core.errors import Error
from ..core import const


def class_filter(target):
    def do_match(tag):
        classes = tag.get('class', [])
        return target in classes
    return do_match


def get_content(tag):
    video_tags = tag.find_all(class_filter('video'))
    if video_tags:
        return video_tags[0].find_all('source')[0].get('src')
    else:
        img_tags = tag.find_all(class_filter('img'))
        return img_tags[0].get("data-src")


class EromeExtractor(BaseExtractor):

    url_key = ['erome']

    def __init__(self, post, **kwargs):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the Erome website via
        BeautifulSoup4.
        """
        super().__init__(post, **kwargs)

    def extract_content(self):
        try:
            if self.url.lower().endswith(const.ALL_EXT):
                self.extract_direct_link()
            else:
                self.extract_album()
        except Exception:
            message = 'Failed to locate content'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message)

    def get_soup(self):
        soup = BeautifulSoup(self.get_text(self.url), 'html.parser')
        return soup

    def extract_single(self):
        # Singles are just ablums containing 1 item
        pass

    def extract_album(self):
        soup = BeautifulSoup(self.get_text(self.url), 'html.parser')
        album = soup.find_all(class_filter('media-group'))
        urls = [get_content(x) for x in album]
        count = 0
        if len(urls) > 1:
            count = 1
        for url in urls:
            _, hosted_id = url.rsplit('/', 1)
            base, extension = hosted_id.rsplit('.', 1)
            self.make_content(url, extension, count=count if count > 0 else None, media_id=base)
            count += 1
