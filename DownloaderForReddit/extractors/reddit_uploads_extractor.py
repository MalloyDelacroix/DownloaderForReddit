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


import re

from .base_extractor import BaseExtractor
from ..core.errors import Error
from ..core import const
from ..utils import reddit_utils


class RedditUploadsExtractor(BaseExtractor):

    url_key = ['reddituploads', 'i.redd.it', 'reddit.com/gallery']

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)
        self.submission = self.get_host_submission()

    def get_host_submission(self):
        try:
            r = reddit_utils.get_reddit_instance()
            parent_submission = r.submission(self.submission.crosspost_parent.split('_')[1])
            parent_submission.title
            return parent_submission
        except AttributeError:
            return self.submission

    def extract_content(self):
        try:
            if 'gallery' in self.url:
                self.extract_album()
            elif self.url.lower().endswith(const.ALL_EXT):
                self.extract_direct_link()
            else:
                self.extract_single()
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message,
                                       exc_info=True)

    def extract_album(self):
        try:
            count = 1
            for value in self.submission.media_metadata.values():
                try:
                    container = value['s']
                    url = container['u']
                    ext = url[url.rfind('.') + 1: url.rfind('?width')]
                    self.make_content(url, ext, count)
                    count += 1
                except KeyError:
                    # some images in albums are not valid for whatever reason, so we ignore them and move on
                    pass
        except:
            self.handle_failed_extract(
                error=Error.FAILED_TO_EXTRACT,
                message='Failed to extract images from reddit gallery',
                log_exception=True,
            )

    def extract_single(self):
        if not self.url.endswith(const.ALL_EXT):
            self.url = self.url + '.jpg'  # add jpg extension here for direct download
        media_id = self.clean_ext(self.get_link_id())
        self.make_content(self.url, 'jpg')

    def extract_direct_link(self):
        """This is overridden here so that a proper media id can be extracted."""
        ext = self.url.rsplit('.', 1)[1]
        media_id = self.clean_ext(self.get_link_id())
        self.make_content(self.url, ext)

    def get_link_id(self):
        """
        Separates the first part of the link after the domain to be used as the post id.  If this fails, the entire url
        after the domain is returned.
        """
        reg = re.search('(?<=com\/)(.*?)(?=\?)', self.url)
        try:
            return reg.group()
        except AttributeError:
            if '.com' in self.url:
                return self.url.split('.com/', 1)[1]
            else:
                return self.url.rsplit('/', 1)[1]

    @staticmethod
    def clean_ext(link_id):
        if link_id.endswith(const.ALL_EXT):
            return link_id.rsplit('.', 1)[0]
        return link_id
