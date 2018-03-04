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


from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError, ImgurClientRateLimitError

from Extractors.BaseExtractor import BaseExtractor
from Core import Const
from Logging import LogUtils


class ImgurExtractor(BaseExtractor):

    url_key = 'imgur'

    def __init__(self, post, reddit_object, content_display_only=False):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the imgur website through the imgur
        api via ImgurPython

        :param imgur_client: A tuple of the client id and client secret provided by imgur to access their api.  This
        tuple is supplied to imgurpython to establish an imgur client
        """
        super().__init__(post, reddit_object, content_display_only)
        self.imgur_client_id = self.settings_manager.imgur_client_id
        self.imgur_client_secret = self.settings_manager.imgur_client_secret
        if self.imgur_client_id is None or self.imgur_client_secret is None:
            if LogUtils.imgur_client_error_log_count < 1:
                message = 'No valid Imgur client detected.  In order to download content from imgur.com, you must ' \
                          'have a valid imgur client id and client secret.  Please see the imgur client information' \
                          'dialog in the settings menu.'
                self.handle_failed_extract(message=message, imgur_client_id_valid=self.imgur_client_id is not None,
                                           imgur_client_secret_valid=self.imgur_client_secret is not None)
        else:
            try:
                self.client = ImgurClient(self.imgur_client_id, self.imgur_client_secret)
            except ImgurClientError as e:
                if e.status_code == 500:
                    self.over_capacity_error()

    def extract_content(self):
        """Dictates what type of page container a link is and then dictates which extraction method should be used"""
        try:
            if 'i.imgur' in self.url:
                self.extract_direct_link()

            elif "/a/" in self.url:
                self.extract_album()
            elif '/gallery/' in self.url:
                try:
                    self.extract_album()
                except:
                    pass
            elif self.url.lower().endswith(Const.ALL_EXT):
                self.extract_direct_mislinked()
            else:
                self.extract_single()
        except ImgurClientError as e:

            if e.status_code == 403:
                if self.client.credits['ClientRemaining'] is None:
                    self.failed_to_locate_error()
                elif self.client.credits['ClientRemaining'] <= 0:
                    self.no_credit_error()
                else:
                    self.failed_to_locate_error()
            if e.status_code == 429:
                self.rate_limit_exceeded_error()
            if e.status_code == 500:
                self.over_capacity_error()
            if e.status_code == 404:
                self.does_not_exist_error()
        except ImgurClientRateLimitError:
            self.rate_limit_exceeded_error()
        except:
            self.failed_to_locate_error()

    def rate_limit_exceeded_error(self):
        message = 'Imgur rate limit exceeded'
        self.handle_failed_extract(message=message, save=True, imgur_error_message='rate limit exceeded')

    def no_credit_error(self):
        message = 'Not enough imgur credits to extract post'
        self.handle_failed_extract(message=message, save=True, imgur_error_message='not enough credits')

    def over_capacity_error(self):
        message = 'Imgur is currently over capacity'
        self.handle_failed_extract(message=message, save=True, imgur_error_message='over capacity')

    def does_not_exist_error(self):
        message = 'Content does not exist.  This most likely means that the content has been deleted on Imgur but ' \
                  'the post still remains on reddit'
        self.handle_failed_extract(message=message, imgur_error_message='Content does not exist')

    def failed_to_locate_error(self):
        message = 'Failed to locate content'
        self.handle_failed_extract(message=message, extractor_error_message=message)

    def extract_album(self):
        count = 1
        domain, album_id = self.url.rsplit('/', 1)
        for pic in self.client.get_album_images(album_id):
            url = pic.link
            address, extension = url.rsplit('.', 1)
            file_name = self.get_filename(album_id)
            if pic.type == 'image/gif' and pic.animated:
                extension = 'mp4'
                url = pic.mp4
            self.make_content(url, file_name, extension, count)
            count += 1

    def extract_single(self):
        domain, image_id = self.url.rsplit('/', 1)
        pic = self.client.get_image(image_id)
        url = pic.link
        address, extension = url.rsplit('.', 1)
        file_name = self.get_filename(image_id)
        if pic.type == 'image/gif' and pic.animated:
            extension = 'mp4'
            url = pic.mp4
        self.make_content(url, file_name, extension)

    def extract_direct_link(self):
        for ext in Const.ALL_EXT:
            if ext in self.url:
                index = self.url.find(ext)
                url = '%s%s' % (self.url[:index], ext)

        try:
            domain, id_with_ext = url.rsplit('/', 1)
            image_id, extension = id_with_ext.rsplit('.', 1)
            file_name = self.get_filename(image_id)
            if url.endswith('gifv') or url.endswith('gif'):
                picture = self.client.get_image(image_id)
                if picture.type == 'image/gif' and picture.animated:
                    url = picture.mp4
                    extension = 'mp4'
            self.make_content(url, file_name, extension)
        except NameError:
            message = 'Unrecognized extension'
            self.handle_failed_extract(message=message, extractor_error_message=message)

    def extract_direct_mislinked(self):
        """
        All direct links to imgur.com must start with 'https://i.imgur.  Sometimes links get mis labeled somehow when
        they are posted.  This method is to add the correct address beginning to mislinked imgur urls and get a proper
        extraction
        """
        for ext in Const.ALL_EXT:
            if ext in self.url:
                index = self.url.find(ext)
                url = '%s%s' % (self.url[:index], ext)

        try:
            domain, id_with_ext = url.rsplit('/', 1)
            domain = 'https://i.imgur.com/'
            url = '%s%s' % (domain, id_with_ext)
            image_id, extension = id_with_ext.rsplit('.', 1)
            file_name = self.get_filename(image_id)
            if url.endswith('gifv') or url.endswith('gif'):
                picture = self.client.get_image(image_id)
                if picture.type == 'image/gif' and picture.animated:
                    url = picture.mp4
                    extension = 'mp4'
            self.make_content(url, file_name, extension)
        except NameError:
            message = 'Unrecognized extension'
            self.handle_failed_extract(message=message, extractor_error_message=message)
