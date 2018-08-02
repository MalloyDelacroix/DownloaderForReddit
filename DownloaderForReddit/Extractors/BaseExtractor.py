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
import Utils.Injector
from Core.Post import Post


class BaseExtractor:

    url_key = (None, )

    def __init__(self, post, reddit_object, content_display_only=False):
        """
        A base class for extracting downloadable urls from container websites.  This class should be overridden and any
        necessary methods overridden by subclasses to perform link extraction from the target website.  Each subclass
        must also include the url_key parameter which is used for matching the website url to the extractor to be used.

        :param post: The praw post object which is a post taken from reddit.  This is used to supply specific post
                     related information to the content items that are created.
        :param reddit_object: The reddit object for which content is being extracted.  This is used to supply reddit
                              object specific information to the content items that are created
        :param content_display_only: Bool value that tells whether the content created will be for display purposes
                                     only.  This is used by the UserFinder module and defaults to False.
        :type post: Praw.Post
        :type reddit_object: RedditObject
        :type content_display_only: bool
        """
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.settings_manager = Utils.Injector.get_settings_manager()
        self.url = post.url
        self.domain = post.domain
        self.user = post.author
        self.post_title = post.title
        self.subreddit = post.subreddit if not reddit_object.object_type == 'SUBREDDIT' else reddit_object.name
        self.creation_date = post.created
        self.save_path = reddit_object.save_directory
        self.content_display_only = content_display_only
        self.subreddit_save_method = reddit_object.subreddit_save_method
        self.name_downloads_by = reddit_object.name_downloads_by
        self.extracted_content = []
        self.failed_extract_posts = []
        self.failed_extracts_to_save = []

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
        return self.post_title if self.name_downloads_by == 'Post Title' else media_id

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

    def handle_failed_extract(self, message=None, save=False, log=True, **kwargs):
        """
        Handles the logging and output of error messages encountered while extracting content and saves posts if
        instructed to do so.
        :param message: Supplied text to describe the error that occurred if necessary.  Will only be added to the end of
                        the main window output.
        :param save: Indicates whether the post should be saved or not.  Posts should only be saved for error such as
                     connection errors that are not likely to be repeated on subsequent runs.
        :param log: Indicates whether this failed extract should be logged or not.  This should be used to prevent
                    log spamming for extraction errors that are likely to happen very frequently (such as imgur rate
                    limit error)
        :type message: str
        :type save: bool
        :type log: bool
        :param kwargs: These are keyword arguments that are put into the 'extra' dictionary in the log.  These should be
                       any other parameters that will be helpful in diagnosing problems from the log if an error is
                       encountered.
        """
        message_text = ': %s' % message if message else ''
        failed_post = Post(self.url, self.user.name, self.post_title, self.subreddit.display_name, self.creation_date,
                           status=message if message_text else 'Failed')
        extra = {'extractor_data': self.get_log_data()}
        if save and self.settings_manager.save_failed_extracts:
            self.save_failed_extract()
            message_text += ': This post has been saved and will be downloaded during the next run'
            extra['post_saved'] = True
            failed_post.save_status = 'Saved'

        self.failed_extract_posts.append(failed_post)
        for key, value in kwargs.items():
            extra[key] = value
        if log:
            self.logger.error('Failed to extract content', extra=extra)

    def save_failed_extract(self):
        """
        Saves a failed extract as a Post object to be retried upon future runs.  This should only be done for certain
        errors, such as an over capacity error, that are very likely to not be encountered again on future runs.
        """
        self.failed_extracts_to_save.append(Post(self.url, self.user.name, self.post_title, self.subreddit.display_name,
                                                 self.creation_date))

    def get_log_data(self):
        """
        Returns a loggable dictionary of the extractors current variables to be put into the log.
        """
        return {'url': self.url,
                'user': self.user.name,
                'subreddit': self.subreddit.display_name,
                'post_title': self.post_title,
                'creation_date': self.creation_date,
                'save_path': self.save_path,
                'content_display_only': self.content_display_only,
                'subreddit_save_method': self.subreddit_save_method,
                'name_downloads_by': self.name_downloads_by,
                'extracted_content_count': len(self.extracted_content),
                'failed_extract_message_count': len(self.failed_extract_posts),
                'failed_extracts_to_save_count': len(self.failed_extracts_to_save)}
