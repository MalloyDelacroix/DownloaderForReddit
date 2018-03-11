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


import logging

from Extractors.BaseExtractor import BaseExtractor
from Extractors.DirectExtractor import DirectExtractor
from Core import Injector
from Core import Const


class Extractor:

    def __init__(self, reddit_object):
        """
        Extracts content from hosting websites obtained from links that are posted to reddit.  Responsible for assigning
        the extractor object to be used, calling the necessary methods to extract the content, handling failed extract
        messages and logging, and storing extracted content in the supplied reddit objects content list.
        :param reddit_object: The reddit object for which contains lists of posts to be extracted.
        :type reddit_object: RedditObject
        """
        self.settings_manager = Injector.get_settings_manager()
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.reddit_object = reddit_object

    def run(self):
        for post in self.reddit_object.saved_submissions:
            self.extract(post)
        for post in self.reddit_object.new_submissions:
            self.extract(post)

    def extract(self, post):
        """
        Creates the proper extractor object and calls its extract method, then handles the extractions.
        :param post: The post that is to be extracted.
        :type post: Praw.Post
        """
        self.reddit_object.set_date_limit(post.created)
        try:
            extractor = self.assign_extractor(post)(post, self.reddit_object)
            extractor.extract_content()
            self.handle_content(extractor)
        except TypeError:
            self.reddit_object.failed_extracts.append('Failed to extract post: Url domain not supported\n'
                                                      'Url: %s, User: %s, Subreddit: %s, Title: %s' %
                                                      (post.url, post.author, post.subreddit, post.title))
            self.logger.error('Failed to find extractor for domain', extra={'url': post.url,
                                                                            'reddit_object': self.reddit_object.json})

    def get_subreddit(self, post):
        """
        Method returns the subreddit the post was submitted in if the reddit object type is not subreddit, otherwise
        the reddit objects name is used.  This is done so that folder names for subreddit downloads match the user
        entered subreddit names capitalization wise.  If this is not used subreddit download folders capitalization may
        not match the subreddit object in the list and therefore the downloaded content view may not work correctly.
        :param post: The post taken from reddit.
        :type post: praw.Post
        :return: The name of the subreddit as it is to be used in the download process.
        :rtype: str
        """
        return post.subreddit if self.reddit_object.object_type != 'SUBREDDIT' else self.reddit_object.name

    def assign_extractor(self, post):
        """
        Selects and returns the extractor to be used based on the url of the supplied post.
        :param post: The post that is to be extracted.
        :type post: praw.Post
        :return: The extractor that is to be used to extract content from the supplied post.
        :rtype: BaseExtractor
        """
        for extractor in BaseExtractor.__subclasses__():
            key = extractor.get_url_key()
            if key is not None and key in post.url.lower():
                return extractor
        if post.url.lower().endswith(Const.ALL_EXT):
            return DirectExtractor
        return None

    def handle_content(self, extractor):
        """
        Takes the appropriate action for content that was extracted or failed to extract.
        :param extractor: The extractor that contains the extracted content.
        :type extractor: BaseExtractor
        """
        self.save_submissions(extractor)
        for x in extractor.failed_extract_messages:
            self.reddit_object.failed_extracts.append(x)
        for content in extractor.extracted_content:
            if type(content) == str and content.startswith('Failed'):
                self.reddit_object.failed_extracts.append(content)
            else:
                if self.filter_content(content):
                    self.reddit_object.content.append(content)
                    self.reddit_object.previous_downloads.append(content.url)

    def save_submissions(self, extractor):
        """
        Saves any content that need to be saved.  A check is performed to make sure the content is not already in the
        saved list.
        :param extractor: The extractor that contains the content to be saved.
        :type extractor: BaseExtractor
        """
        for x in extractor.failed_extracts_to_save:
            if not any(x.url == y.url for y in self.reddit_object.saved_submissions):
                self.reddit_object.saved_submissions.append(x)

    def filter_content(self, content):
        """
        Checks the various content filters to see if the supplied content meets the filter standards.
        :param content: The content that is to be filtered.
        :type content: Content
        :return: True or false depending on if the content passes or fails the filter.
        :rtype: bool
        """
        return self.check_image(content) and self.check_video(content) and self.check_duplicate(content)

    def check_image(self, content):
        return self.reddit_object.download_images or not content.endswith(Const.IMAGE_EXT)

    def check_video(self, content):
        return self.reddit_object.download_videos or not content.endswith(Const.VID_EXT)

    def check_duplicate(self, content):
        return not self.reddit_object.avoid_duplicates or content.url not in self.reddit_object.previous_downloads
