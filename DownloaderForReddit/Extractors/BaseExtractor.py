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


import requests
import logging

from Core.Content import Content
import Core.Injector
from Core.Post import Post


class BaseExtractor(object):

    def __init__(self, url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                 save_path, content_display_only=False):
        """
        A class that handles extracting individual item urls from the hosting websites.  Interacts with website APIs if
        available and directly with requests if not.

        :param url: The url of the link posted to reddit
        :param user: The name of the user that posted the link to reddit
        :param post_title: The title of the post that was submitted to reddit
        :param subreddit: The subreddit the post was submitted to
        :param creation_date: The date when the post was submitted to reddit
        """
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.settings_manager = Core.Injector.get_settings_manager()
        self.url = url
        self.user = user
        self.post_title = post_title
        self.subreddit = subreddit
        self.creation_date = creation_date
        self.save_path = save_path
        self.content_display_only = content_display_only
        self.subreddit_save_method = subreddit_save_method
        self.name_downloads_by = name_downloads_by
        self.extracted_content = []
        self.failed_extract_messages = []
        self.failed_extracts_to_save = []

    def extract_content(self):
        """
        Method that dictates which extraction method will be used.  Responsible for deciding how an extractor is
        chosen based on the particular website.
        """
        pass

    def extract_single(self):
        """
        Extracts a single piece of content from a website container.  This is not used to extract direct urls (urls that
        that are the actual url that is downloaded) but to extract the direct url from a container page that is common
        among content hosting websites.
        """
        pass

    def extract_album(self):
        """
        Extracts multiple pieces of content from a single page.  The album format is very common and different hosting
        websites have different methods of accessing the sequential items in an album page.  This method should
        extract each item in an album, assign it a sequential number and add it to the content list.
        """
        pass

    def extract_direct_link(self):
        """
        Extracts information from a link to a downloadable url.  This is a url that ends in the extension of the file
        to be saved.  This method is tried when no other extractors are found for the website domain of a given url.
        """
        domain, id_with_ext = self.url.rsplit('/', 1)
        image_id, extension = id_with_ext.rsplit('.', 1)
        file_name = self.post_title if self.name_downloads_by == 'Post Title' else image_id
        self.make_content(self.url, file_name, None, extension)

    def get_json(self, url):
        """Makes sure that a request is valid and handles without errors if the connection is not successful"""
        response = requests.get(url)
        if response.status_code == 200 and 'json' in response.headers['Content-Type']:
            return response.json()
        else:
            self.handle_failed_extract(message='Failed to retrieve json data from link',
                                       response_code=response.status_code)

    def get_text(self, url):
        """See get_json"""
        response = requests.get(url)
        if response.status_code == 200 and 'text' in response.headers['Content-Type']:
            return response.text
        else:
            self.handle_failed_extract(message='Failed to retrieve data from link', response_code=response.status_code)

    def make_content(self, url, file_name, extension, count=None):
        """
        Takes content elements that are extracted and creates a Content object with the extracted parts and the global
        extractor items, then sends the new Content object to the extracted content list.
        :param url: The url of the content item.
        :param file_name: The file name of the content item, either the post name or the album id depending on user
                          settings.
        :param count: The number in an album sequence that the supplied url belongs.  Used to number the file.
        :param extension: The extension of the supplied url and the url used for the downloaded file.
        :type url: str
        :type file_name: str
        :type extension: str
        :type count: int
        """
        count = ' %s' % count if count else ''
        x = Content(url, self.user, self.post_title, self.subreddit, file_name, count, '.' + extension, self.save_path,
                    self.subreddit_save_method, self.creation_date, self.content_display_only)
        self.extracted_content.append(x)

    def handle_failed_extract(self, message=None, save=False, **kwargs, ):
        """
        Handles the messages, logging, and saving of content that failed to extract.
        """
        message_text = ': %s' % message if message else ''
        extra = {'extractor_data': self.get_log_data()}
        if save and self.settings_manager.save_failed_extracts:
            self.save_failed_extract()
            message_text += ': This post has been saved and will be downloaded during the next run'
            extra['post_saved'] = True

        self.failed_extract_messages.append('Failed to extract content: User: %s Subreddit: %s Title: %s Url: %s%s' %
                                            (self.user, self.subreddit, self.post_title, self.url, message_text))
        for key, value in kwargs.items():
            extra[key] = value
        self.logger.error('Failed to extract content', extra=extra)

    def save_failed_extract(self):
        """
        Saves a failed extract as a Post object to be retried upon future runs.  This should only be done for certain
        errors, such as an over capacity error, that are very likely to not be encountered again on future runs.
        """
        self.failed_extracts_to_save.append(Post(self.url, self.user, self.post_title, self.subreddit,
                                                 self.creation_date))

    def get_log_data(self):
        return {'url': self.url,
                'user': self.user,
                'subreddit': self.subreddit,
                'post_title': self.post_title,
                'creation_date': self.creation_date,
                'save_path': self.save_path,
                'content_display_only': self.content_display_only,
                'subreddit_save_method': self.subreddit_save_method,
                'name_downloads_by': self.name_downloads_by,
                'extracted_content_count': len(self.extracted_content),
                'failed_extract_message_count': len(self.failed_extract_messages),
                'failed_extracts_to_save_count': len(self.failed_extracts_to_save)}
