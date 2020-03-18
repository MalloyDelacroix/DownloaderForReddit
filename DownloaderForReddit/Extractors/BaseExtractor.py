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
from ..Database.ModelEnums import DownloadNameMethod, SubredditSaveStructure


class BaseExtractor:

    url_key = (None, )

    def __init__(self, post):
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
        self.post_title = post.title
        self.url = post.url
        self.domain = post.domain
        self.user = post.author
        self.subreddit = post.subreddit
        self.creation_date = post.date_posted
        self.extracted_content = []
        self.failed_extraction = False
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

    @property
    def significant_reddit_object(self):
        """
        Returns the reddit object for which the extraction is being performed.  This is calculated by checking which of
        the posts reddit objects is significant and returning that reddit object. Defaults to the posts author.
        """
        if self.user.significant:
            return self.user
        elif self.subreddit.significant:
            return self.subreddit
        return self.user

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
        file_name = self.get_filename(media_id)
        self.make_content(self.url, file_name, extension)

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

    def get_filename(self, media_id):
        """
        Checks the settings manager to determine if the post title or the content id (as stored on the container site)
        should be used to name the content that is being extracted.
        :param media_id: The image/album/video id as stored on a container site.
        :type media_id: str
        :return: The file name that should be used when creating the Content object from the extracted url.
        :rtype: str
        """
        reddit_object = self.significant_reddit_object
        method = reddit_object.download_naming_method
        if method == DownloadNameMethod.id:
            return media_id
        elif method == DownloadNameMethod.title:
            return self.post_title
        else:
            self.use_count = False  # specify not to use album item count when incrementing by number of downloads
            return f'{reddit_object.name} {reddit_object.get_post_count()}'

    def make_content(self, url, file_name, extension, count=None):
        """
        Takes content elements that are extracted and creates a Content object with the extracted parts and the global
        extractor items, then sends the new Content object to the extracted content list.
        :param url: The url of the content item.
        :param file_name: The file name of the content item, either the post name or the album id depending on user
                          settings.
        :param count: The number in an album sequence that the supplied url belongs.  Used to number the file.
        :param extension: The extension of the supplied url and the url used for the downloaded file.
        :return: The content object that was created.
        :type url: str
        :type file_name: str
        :type extension: str
        :type count: int
        :rtype: Content
        """
        if self.check_duplicate_content(url):
            count = f' {count}' if count and self.use_count else ''
            title = file_name + count
            dir_path = self.make_dir_path()
            content = Content(
                title=title,
                extension=extension,
                url=url,
                user=self.user,
                subreddit=self.subreddit,
                post=self.post,
                directory_path=dir_path
            )
            self.extracted_content.append(content)
            # TODO: need to figure out best way to set directory_path before content is saved
            return content
        return None

    def make_dir_path(self):
        """
        Creates and returns the path for the directory the content should be saved in based on the user set base save
        directory and the content's significant reddit object type and subreddit save structure.
        :return: The path to the directory in which the content item being created will be saved.
        """
        significant_ro = self.post.significant_reddit_object
        if significant_ro.object_type == 'USER':
            return os.path.join(self.settings_manager.user_save_directory, significant_ro.name)
        else:
            if significant_ro.subreddit_save_structure == SubredditSaveStructure.sub_name:
                joiner = self.subreddit.name
            elif significant_ro.subreddit_save_structure == SubredditSaveStructure.author_name:
                joiner = self.user.name
            elif significant_ro.subreddit_save_structure == SubredditSaveStructure.sub_name_author_name:
                joiner = os.path.join(self.subreddit.name, self.user.name)
            else:
                joiner = os.path.join(self.user.name, self.subreddit.name)
            return os.path.join(self.settings_manager.subreddit_save_directory, joiner)

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
        self.post.set_extraction_failed(message)
        extra = {'extractor_data': self.get_log_data()}
        extra.update(kwargs)
        if log:
            self.logger.error(f'Failed to extract content: {message}', extra=extra, exc_info=log_exception)

    def get_log_data(self):
        """
        Returns a loggable dictionary of the extractors current variables to be put into the log.
        """
        return {
            'url': self.url,
            'user': self.user.name,
            'subreddit': self.subreddit.name,
            'post_title': self.post_title,
            'creation_date': self.creation_date,
            'extracted_content_count': len(self.extracted_content),
            'extraction_failed': self.failed_extraction,
        }
