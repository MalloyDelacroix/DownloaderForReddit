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

from .base_extractor import BaseExtractor
from ..utils import imgur_utils, ImgurError
from ..core.errors import Error
from ..core import const


class ImgurExtractor(BaseExtractor):

    url_key = ['imgur']

    def __init__(self, post, **kwargs):
        """
        A subclass of the BaseExtractor class.  This class interacts exclusively with the imgur website through the
        imgur api via ImgurPython
        """
        super().__init__(post, **kwargs)

    def extract_content(self):
        """Dictates what type of page container a link is and then dictates which extraction method should be used"""
        self.url = self.filter_url(self.url)
        try:
            if "/a/" in self.url or '/t/' in self.url:  # album extraction is tested for first because of incorrectly formatted urls
                self.extract_album()
            elif self.url.lower().endswith(const.ALL_EXT):
                self.extract_direct_link()
            elif '/gallery/' in self.url:
                self.extract_album()
            else:
                self.extract_single()
        except ImgurError as e:
            self.handle_client_error(e.status_code)
        except Exception:
            message = 'Failed to extract content'
            self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message,
                                       extractor_error_message=message, log_exception=True)

    def filter_url(self, url):
        """
        Filter characters out of the supplied url that cause problems when trying to extract.
        :param url: The url that is to be cleaned.
        :return: The usable part of the supplied url if it contains certain characters or the whole url if it does not.
        """
        if '?' in url:
            return url.split('?')[0]
        if '#' in url:
            return url.split('#')[0]
        if url.endswith('/'):
            url = url[:-1]
        return url

    def extract_album(self):
        count = 1
        _, album_id = self.url.rsplit('/', 1)
        for url in imgur_utils.get_album_images(album_id):
            url = self.filter_url(url)
            _, extension = url.rsplit('.', 1)
            self.make_content(url, extension, count)
            count += 1

    def extract_single(self):
        _, image_id = self.url.rsplit('/', 1)
        url = imgur_utils.get_single_image(image_id)
        _, extension = url.rsplit('.', 1)
        self.make_content(url, extension)

    def extract_direct_link(self):
        try:
            url = self.get_direct_url()
            domain, id_with_ext = url.rsplit('/', 1)
            image_id, extension = id_with_ext.rsplit('.', 1)
            if extension == 'gif':
                extension = 'mp4'
            url = "{}/{}.{}".format(domain, image_id, extension)
            self.make_content(url, extension)
        except (AttributeError, NameError, TypeError):
            message = 'Unrecognized extension'
            self.handle_failed_extract(error=Error.UNRECOGNIZED_EXTENSION, message=message,
                                       extractor_error_message=message)

    def handle_client_error(self, status_code):
        """
        Handles logging and reporting of errors that are reported by the imgur client.  These errors are handled
        separately from other errors because they contain more meaningful information because Imgur provides the status
        code of the error and the meaning of the status code.
        :param status_code: The error status code as reported by imgur.
        :type status_code: int
        """
        if status_code == 403:
            self.forbidden_error()
        elif status_code == 429:
            self.rate_limit_exceeded_error()
        elif status_code == 500:
            self.over_capacity_error()
        elif status_code == 404:
            self.does_not_exist_error()
        else:
            self.unknown_connection_error(status_code)

    def rate_limit_exceeded_error(self):
        """
        Handles a rate limit error reported from imgur.  The rate limit error can indicate too many api calls are being
        called in too short of a window (attempts are made to mitigate this by the application) or that the user is out
        of imgur user credits.
        """
        if imgur_utils.check_credits() <= 0:
            message = 'Out of user credits'
            error = Error.CREDIT_ERROR
        else:
            message = 'Imgur rate limit exceeded'
            error = Error.RATE_LIMIT_ERROR
        self.handle_failed_extract(error=error, message=message, imgur_error_message='rate limit exceeded',
                                   log_exception=True)

    def no_credit_error(self):
        message = 'Not enough imgur credits to extract post'
        self.handle_failed_extract(error=Error.CREDIT_ERROR, message=message, imgur_error_message='not enough credits',
                                   log_exception=True)

    def over_capacity_error(self):
        message = 'Imgur is currently over capacity'
        self.handle_failed_extract(error=Error.UNSUCCESSFUL_RESPONSE, message=message,
                                   imgur_error_message='over capacity')

    def does_not_exist_error(self):
        message = 'Content does not exist.'
        self.handle_failed_extract(error=Error.DOES_NOT_EXIST, message=message,
                                   imgur_error_message='Content does not exist')

    def forbidden_error(self):
        message = 'Forbidden'
        self.handle_failed_extract(error=Error.FORBIDDEN, message=message, extractor_error_message=message)

    def failed_to_locate_error(self):
        message = 'Failed to locate content'
        self.handle_failed_extract(error=Error.FAILED_TO_LOCATE, message=message, extractor_error_message=message,
                                   log_exception=True)

    def unknown_connection_error(self, status_code):
        message = 'Unknown imgur connection error'
        self.handle_failed_extract(error=Error.UNKNOWN_ERROR, message=message, status_code=status_code,
                                   log_exception=True)

    def get_direct_url(self):
        """
        Checks to make sure the url extension is a recognized media extension and also checks if the url is mislinked.
        :return: The correct url if the extension is valid, None if not.
        :rtype: str
        """
        for ext in const.ALL_EXT:
            if ext in self.url:
                index = self.url.find(ext)
                url = self.url[:index] + ext
                return url
        return None
