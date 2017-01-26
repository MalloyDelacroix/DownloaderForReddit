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

from Content import Content
from Extractors import ImgurExtractor, GfycatExtractor, VidbleExtractor, EroshareExtractor, RedditUploadsExtractor


class RedditObject(object):

    def __init__(self, name, save_path, imgur_client, post_limit, name_downloads_by, avoid_duplicates, download_videos,
                 download_images, user_added):
        """
        Class that holds the name and list of submissions for Reddit objects.  Also contains an empty content list that
        will be filled with Content objects that contain links for download.

        :param name: The name of the user or subreddit which is to be extracted from
        :param new_submissions: A list of submissions as PRAW objects containing all the reddit data extracted by PRAW

        :date_limit: This is set to the most recent download for the user/sub and cannot be changed by the end user
        :custom_date_limit: This is used as a way to override the date_limit variable without losing the last date that
        the user/sub had content.  If this variable is anything but 'None' it will be considered. If a user/sub setting
        is set to not restrict download date, it becomes 1.
        """
        self.name = name
        self.subreddit_save_method = None
        self.save_path = save_path
        self.imgur_client = imgur_client
        self.post_limit = post_limit
        self.name_downloads_by = name_downloads_by
        self.avoid_duplicates = avoid_duplicates
        self.download_videos = download_videos
        self.download_images = download_images
        self.user_added = user_added
        self.do_not_edit = False
        self.new_submissions = None  # Will be erased at end of download
        self.already_downloaded = []
        self.date_limit = 1
        self.custom_date_limit = None
        self.content = []  # Will be erased at end of download
        self.failed_extracts = []  # This will be erased at the end of download
        self.number_of_downloads = len(self.already_downloaded)

    def extract_content(self):
        for post in self.new_submissions:
            if "imgur" in post.url:
                if self.imgur_client[0] is None or self.imgur_client[1] is None:
                    self.failed_extracts.append('Failed: No valid Imgur client is detected. In order to download '
                                                'content from imgur.com you must have a valid Imugr client. Please see'
                                                'the settings menu.\nTitle: %s,  User: %s,  Subreddit: %s,  URL: %s' %
                                                (post.title, post.author, post.subreddit, post.url))
                else:
                    imgur_extractor = ImgurExtractor(post.url, post.author, post.title, post.subreddit, self.save_path,
                                                     self.subreddit_save_method, self.imgur_client,
                                                     self.name_downloads_by)
                    imgur_extractor.extract_content()
                    for x in imgur_extractor.extracted_content:
                        if type(x) == str and x.startswith('Failed'):
                            self.failed_extracts.append(x)
                        else:
                            if not self.avoid_duplicates or x.url not in self.already_downloaded:
                                if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                                    if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                                   '.webm', '.png')):
                                        self.content.append(x)
                                        self.already_downloaded.append(x.url)

            elif "vidble" in post.url:
                vidble_extractor = VidbleExtractor(post.url, post.author, post.title, post.subreddit, self.save_path,
                                                   self.subreddit_save_method, self.name_downloads_by)
                vidble_extractor.extract_content()
                for x in vidble_extractor.extracted_content:
                    if type(x) == str and x.startswith('Failed'):
                        self.failed_extracts.append(x)
                    else:
                        if not self.avoid_duplicates or x.url not in self.already_downloaded:
                            if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                                if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                               '.webm', '.png')):
                                    self.content.append(x)
                                    self.already_downloaded.append(x.url)

            elif "gfycat" in post.url:
                gfycat_extractor = GfycatExtractor(post.url, post.author, post.title, post.subreddit, self.save_path,
                                                   self.subreddit_save_method, self.name_downloads_by)
                gfycat_extractor.extract_content()
                for x in gfycat_extractor.extracted_content:
                    if type(x) == str and x.startswith('Failed'):
                        self.failed_extracts.append(x)
                    else:
                        if not self.avoid_duplicates or x.url not in self.already_downloaded:
                            if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                                if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                               '.webm', '.png')):
                                    self.content.append(x)
                                    self.already_downloaded.append(x.url)

            elif "eroshare" in post.url:
                eroshare_extractor = EroshareExtractor(post.url, post.author, post.title, post.subreddit,
                                                       self.save_path, self.subreddit_save_method,
                                                       self.name_downloads_by)
                eroshare_extractor.extract_content()
                for x in eroshare_extractor.extracted_content:
                    if type(x) == str and x.startswith('Failed'):
                        self.failed_extracts.append(x)
                    else:
                        if not self.avoid_duplicates or x.url not in self.already_downloaded:
                            if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                                if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                               '.webm', '.png')):
                                    self.content.append(x)
                                    self.already_downloaded.append(x.url)

            elif "reddituploads" in post.url:
                pass
                reddit_uploads_extractor = RedditUploadsExtractor(post.url, post.author, post.title, post.subreddit,
                                                                  self.save_path, self.subreddit_save_method,
                                                                  self.name_downloads_by)
                reddit_uploads_extractor.extract_content()
                for x in reddit_uploads_extractor.extracted_content:
                    if type(x) == str and x.startswith('Failed'):
                        self.failed_extracts.append(x)
                    else:
                        if not self.avoid_duplicates or x.url not in self.already_downloaded:
                            if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                                if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                               '.webm', '.png')):
                                    self.content.append(x)
                                    self.already_downloaded.append(x.url)

            elif post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4', '.webm', '.wmv')):
                domain, id_with_ext = post.url.rsplit('/', 1)
                image_id, extension = id_with_ext.rsplit('.', 1)
                file_name = post.title if self.name_downloads_by == 'Post Title' else image_id
                x = Content(post.url, post.author, post.title, post.subreddit, file_name, "", '.' + extension,
                            self.save_path, self.subreddit_save_method)
                if not self.avoid_duplicates or x.url not in self.already_downloaded:
                    if self.download_videos or not x.url.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx')):
                        if self.download_images or not x.url.endswith(('.jpg', '.jpeg', '.gif', '.gifv',
                                                                       '.webm', '.png')):
                            self.content.append(x)
                            self.already_downloaded.append(x.url)

            else:
                self.failed_extracts.append("Could not extract links from post: %s submitted by: %s\nUrl domain not "
                                            "supported.  Url: %s" % (post.title, post.author, post.url))

            self.set_date_limit(post.created)

    def set_date_limit(self, last_download_time):
        if self.date_limit is not None and last_download_time > self.date_limit:
            self.date_limit = last_download_time
        elif self.date_limit is None:
            self.date_limit = last_download_time

    def get_new_submissions(self, submissions):
        self.new_submissions = submissions

    def check_save_path(self):
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)

    def clear_download_session_data(self):
        self.content.clear()
        self.new_submissions = None
        self.failed_extracts.clear()

    def update_post_limit(self, new_limit):
        if not self.do_not_edit:
            self.post_limit = new_limit

    def update_imgur_client(self, new_imgur_client):
        self.imgur_client = new_imgur_client

    def update_name_downloads_by(self, new_method):
        if not self.do_not_edit:
            self.name_downloads_by = new_method

    def update_avoid_duplicates(self, state):
        if not self.do_not_edit:
            self.avoid_duplicates = state

    def update_custom_date_limit(self, new_limit):
        if not self.do_not_edit:
            if new_limit == 0:
                self.custom_date_limit = None
            else:
                self.custom_date_limit = new_limit

    def update_number_of_downloads(self):
        self.number_of_downloads = len(self.already_downloaded)


class User(RedditObject):

    def __init__(self, name, save_path, imgur_client, post_limit, name_downloads_by, avoid_duplicates, download_videos,
                 download_images, user_added):
        """
        A subclass of the RedditObject class.  This class is used exclusively to hold users and their information
        """
        super().__init__(name, save_path, imgur_client, post_limit, name_downloads_by, avoid_duplicates,
                         download_videos, download_images, user_added)
        self.save_path = "%s%s/" % (self.save_path, self.name)
        self.subreddit_save_method = None
        self.imgur_client = imgur_client

    def update_save_path(self, save_path):
        self.save_path = "%s%s%s" % (save_path, self.name, '/' if not save_path.endswith('/') else '')


class Subreddit(RedditObject):

    def __init__(self, name, save_path, post_limit, subreddit_save_method, imgur_client, name_downloads_by,
                 avoid_duplicates, download_videos, download_images, user_added):
        """
        A subclass of the RedditObject class. This class is used exclusively to hold subreddits and their information.
        Also contains an extra method not used for users to update the subreddit_save_by_method
        """
        super().__init__(name, save_path, imgur_client, post_limit, name_downloads_by, avoid_duplicates,
                         download_videos, download_images, user_added)
        self.subreddit_save_method = subreddit_save_method
        self.imgur_client = imgur_client

    def update_save_path(self, save_path):
        self.save_path = save_path

    def update_subreddit_save_by_method(self, new_method):
        self.subreddit_save_method = new_method
