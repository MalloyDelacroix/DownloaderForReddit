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

import os
import requests
import logging

from ..Database.Models import Content, Post
from ..Utils import Injector
from ..Utils.TokenParser import TokenParser
from ..Messaging.Message import Message


class BaseExtractor:

    url_key = (None, )

    def __init__(self, post, **kwargs):
        """
        A base class for extracting downloadable urls from container websites.  This class should be overridden and any
        necessary methods overridden by subclasses to perform link extraction from the target website.  Each subclass
        must also include the url_key parameter which is used for matching the website url to the extractor to be used.

        :param post: The post object created from the submission extracted from reddit.
        :type post: Post
        """
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.settings_manager = Injector.get_settings_manager()
        self.post = post
        self.comment = kwargs.get('comment', None)
        self.url = kwargs.get('url', post.url)
        self.user = kwargs.get('user', post.author)
        self.subreddit = kwargs.get('subreddit', post.subreddit)
        self.significant_reddit_object = kwargs.get('significant_reddit_object', post.significant_reddit_object)
        self.creation_date = kwargs.get('date_posted', post.date_posted)
        self.count = kwargs.get('count', None)
        self.extracted_content = []
        self.failed_extraction = False
        self.failed_extraction_message = None
        self.use_count = True

    def __str__(self):
        return __name__

    @classmethod
    def get_url_key(cls):
        """
        Returns the url_key that each subclass must contain.  The url_key is used to indicate keywords that are domain
        specific.  The url_key must be so that if the extractor finds the key in a supplied url, the extractor object
        to which the key belongs can be selected to perform the link extraction.
        :return: A key that that if found in a url means this extractor is selected to be used for link extraction.
        :rtype: str
        """
        return cls.url_key

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
        In most cases it is not necessary to override this method in a sub class.  All direct link extraction should be
        the same and subclasses can call this method directly.  There are some cases where this is not the case and
        this method must be overwritten.
        """
        domain, id_with_ext = self.url.rsplit('/', 1)
        media_id, extension = id_with_ext.rsplit('.', 1)
        self.make_content(self.url, extension)

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

    def make_content(self, url, extension, count=None, name_modifier=''):
        """
        Takes content elements that are extracted and creates a Content object with the extracted parts and the global
        extractor items, then sends the new Content object to the extracted content list.
        :param url: The url of the content item.
        :param count: The number in an album sequence that the supplied url belongs.  Used to number the file.
        :param extension: The extension of the supplied url and the url used for the downloaded file.
        :return: The content object that was created.
        :type url: str
        :type extension: str
        :type count: int
        :rtype: Content
        """
        if self.check_duplicate_content(url):
            if count is None:
                count = self.count
            count = f' {count}' if count and self.use_count else ''
            title = f'{self.make_title()}{name_modifier}{count}'
            directory = self.make_dir_path()
            content = Content(
                title=title,
                extension=extension,
                url=url,
                user=self.user,
                subreddit=self.subreddit,
                post=self.post,
                directory_path=directory
            )
            session = self.post.get_session()
            session.add(content)
            session.commit()
            self.extracted_content.append(content)
            return content
        return None

    def make_title(self):
        if self.comment is None:
            token_string = self.significant_reddit_object.post_download_naming_method
            title = TokenParser.parse_tokens(self.post, token_string)
        else:
            token_string = self.significant_reddit_object.comment_naming_method
            title = TokenParser.parse_tokens(self.comment, token_string)
        return title

    def make_dir_path(self):
        if self.comment is None:
            token_string = self.significant_reddit_object.post_save_structure
            sub_path = TokenParser.parse_tokens(self.post, token_string)
        else:
            token_string = self.significant_reddit_object.comment_save_structure
            sub_path = TokenParser.parse_tokens(self.comment, token_string)
        if self.significant_reddit_object.object_type == 'USER':
            base = self.settings_manager.user_save_directory
        else:
            base = self.settings_manager.subreddit_save_directory
        return os.path.join(base, sub_path)

    def check_duplicate_content(self, url: str) -> bool:
        """
        Checks the supplied contents url to see if content with the same url already exists in the database.
        :param url: The url that will be searched for in the database to see if it already exists.
        :return: True if the content DOES NOT exist in the database, False if the content DOES exist.
        """
        session = self.post.get_session()
        return session.query(Content.id).filter(Content.url == url).scalar() is None

    def get_save_path(self):
        """
        Returns the save path specified in the settings manager based on the type of the significant reddit object.
        """
        if self.significant_reddit_object.object_type == 'USER':
            return self.settings_manager.user_save_directory
        else:
            return self.settings_manager.subreddit_save_directory

    def handle_failed_extract(self, message=None, log=True, log_exception=False, **kwargs):
        """
        Handles the logging and output of error messages encountered while extracting content and saves posts if
        instructed to do so.
        :param message: Supplied text to describe the error that occurred if necessary.  Will only be added to the end
                        of the main window output.
        :param log: Indicates whether this failed extract should be logged or not.  This should be used to prevent
                    log spamming for extraction errors that are likely to happen very frequently (such as imgur rate
                    limit error)
        :param log_exception: If True and log is True, the current exception will be logged if there is one.
        :param kwargs: These are keyword arguments that are put into the 'extra' dictionary in the log.  These should be
                       any other parameters that will be helpful in diagnosing problems from the log if an error is
                       encountered.
        :type message: str
        :type log: bool
        :type log_exception: bool
        """
        self.failed_extraction = True
        self.failed_extraction_message = message
        extra = {'extractor_data': self.get_log_data()}
        extra.update(kwargs)
        if log:
            self.logger.error(f'Failed to extract content: {message}', extra=extra, exc_info=log_exception)
        Message.send_extraction_error(message)

    def get_log_data(self):
        """
        Returns a loggable dictionary of the extractors current variables to be put into the log.
        """
        return {
            'url': self.url,
            'user': self.user.name,
            'subreddit': self.subreddit.name,
            'post_title': self.post.title,
            'extracted_content_count': len(self.extracted_content),
            'extraction_failed': self.failed_extraction,
        }
