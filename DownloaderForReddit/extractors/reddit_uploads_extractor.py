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
        if hasattr(self.submission, 'crosspost_parent'):
            try:
                r = reddit_utils.get_reddit_instance()
                parent_submission = r.submission(self.submission.crosspost_parent.split('_')[1])
                parent_submission.title
                return parent_submission
            except AttributeError:
                pass
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
                    url = self.get_album_item_url(container)
                    ext = self.get_media_extension(url)
                    media_id = getattr(value, 'id', None)
                    self.make_content(url, ext, count, media_id=media_id)
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

    def get_album_item_url(self, container: dict) -> str:
        """
        The url for an album media item will be stored under a different key depending
        on the type of media it is. This method returns the correct url for the media type.
        :param container: The "container" dict for each media item in an album.
        :return: The url to the media item.
        """
        keys = container.keys()
        if 'mp4' in keys:
            return container['mp4']
        if 'gif' in keys:
            return container['gif']
        return container['u']

    def get_media_extension(self, url: str) -> str:
        """
        Extracts the file extension from a URL using regex.
        :param url: The URL to extract the extension from.
        :return: The file extension if found, otherwise None.
        """
        match = re.search(r'\.([a-zA-Z0-9]+)(?=[?#]|$)', url)
        url = match.group(1) if match else ''
        # Reddit encodes gifs as mp4, so if the extension is shown as gif, we return mp4
        if url == 'gif':
            url = 'mp4'
        return url

    def extract_single(self):
        if not self.url.endswith(const.ALL_EXT):
            self.url = self.url + '.jpg'  # add jpg extension here for direct download
        media_id = self.clean_ext(self.get_link_id())
        self.make_content(self.url, 'jpg', media_id=media_id)

    def extract_direct_link(self):
        """This is overridden here so that a proper media id can be extracted."""
        ext = self.url.rsplit('.', 1)[1]
        media_id = self.clean_ext(self.get_link_id())
        self.make_content(self.url, ext, media_id=media_id)

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
