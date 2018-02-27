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


from .Content import Content
from Extractors.Extractor import *
import Core.Injector
from Core import SystemUtil


class RedditObject:

    def __init__(self, version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                 nsfw_filter, name_downlads_by, user_added):
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
        self.version = version
        self.name = name
        self.subreddit_save_method = None
        self.save_path = save_path
        self.post_limit = post_limit
        self.avoid_duplicates = avoid_duplicates
        self.download_videos = download_videos
        self.download_images = download_images
        self.nsfw_filter = nsfw_filter
        self.name_downloads_by = name_downlads_by
        self.user_added = user_added
        self.do_not_edit = False
        self.new_submissions = []  # Will be erased at end of download
        self.saved_submissions = []
        self.previous_downloads = []
        self.date_limit = 86400
        self.custom_date_limit = None
        self.content = []  # Will be erased at end of download (QRunnable objects cannot be pickled)
        self.failed_extracts = []  # This will be erased at the end of download
        self.saved_content = {}
        self.save_undownloaded_content = True
        self.object_type = None
        self.content_display_only = False

    def __str__(self):
        return '%s: %s' % (self.object_type, self.name)

    @property
    def json(self):
        """
        Returns json encodable dict of the reddit objects attributes and and count of the items in the various lists.
        This is used for logging purposes.
        :return: A dict of json encodable attributes.
        :rtype: dict
        """
        return {'name': self.name,
                'object_type': self.object_type,
                'version': self.version,
                'save_path': self.save_path,
                'post_limit': self.post_limit,
                'avoid_duplicates': self.avoid_duplicates,
                'download_videos': self.download_videos,
                'download_images': self.download_images,
                'nsfw_fileter': self.nsfw_filter,
                'added_on': self.user_added,
                'do_not_edit': self.do_not_edit,
                'new_submission_count': len(self.new_submissions) if self.new_submissions is not None else None,
                'saved_submission_count': len(self.saved_submissions),
                'previous_download_count': len(self.previous_downloads),
                'date_limit': self.date_limit,
                'custom_date_limit': self.custom_date_limit,
                'content_count': len(self.content),
                'failed_extract_count': len(self.failed_extracts),
                'saved_content_count': len(self.saved_content)}

    @property
    def number_of_downloads(self):
        return len(self.previous_downloads)

    @property
    def save_directory(self):
        return self.save_path

    def extract_content(self):
        if len(self.saved_submissions) > 0:
            self.assign_extractor(self.saved_submissions)
        if len(self.new_submissions) > 0:
            self.assign_extractor(self.new_submissions)

    def assign_extractor(self, post_list):
        for post in post_list:
            extractor = None
            subreddit = post.subreddit if self.object_type != 'SUBREDDIT' else self.name
            if "imgur" in post.url:
                extractor = ImgurExtractor(post.url, post.author, post.title, subreddit, post.created,
                                           self.subreddit_save_method, self.name_downloads_by, self.save_directory,
                                           self.content_display_only)

            elif "gfycat" in post.url:
                extractor = GfycatExtractor(post.url, post.author, post.title, subreddit, post.created,
                                            self.subreddit_save_method, self.name_downloads_by, self.save_directory,
                                            self.content_display_only)

            elif "vidble" in post.url:
                extractor = VidbleExtractor(post.url, post.author, post.title, subreddit, post.created,
                                            self.subreddit_save_method, self.name_downloads_by, self.save_directory,
                                            self.content_display_only)

            elif "reddituploads" in post.url:
                pass
                extractor = RedditUploadsExtractor(post.url, post.author, post.title, subreddit, post.created,
                                                   self.subreddit_save_method, self.name_downloads_by,
                                                   self.save_directory, self.content_display_only)

            # If none of the extractors have caught the link by here, we check to see if it is a direct link and if so
            # attempt to extract the link directly.  Otherwise the extraction fails due to unsupported domain
            elif post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4', '.webm', '.wmv')):
                extractor = DirectExtractor(post.url, post.author, post.title, subreddit, post.created,
                                            self.subreddit_save_method, self.name_downloads_by, self.save_directory,
                                            self.content_display_only)

            else:
                self.failed_extracts.append("Could not extract links from post: %s submitted by: %s\nUrl domain not "
                                            "supported.  Url: %s" % (post.title, post.author, post.url))

            if extractor:
                self.extract(extractor)

            try:
                self.set_date_limit(post.created)
            except AttributeError:
                pass

    def extract(self, extractor):
        extractor.extract_content()
        for x in extractor.failed_extracts_to_save:
            if not any(x.url == y.url for y in self.saved_submissions):
                self.saved_submissions.append(x)
        for x in extractor.failed_extract_messages:
            print(x)                                                                                # Print statement
            self.failed_extracts.append(x)
        for x in extractor.extracted_content:
            if type(x) == str and x.startswith('Failed'):
                self.failed_extracts.append(x)
            else:
                if self.check_image(x) and self.check_video(x) and self.check_downloaded_content(x):
                    self.content.append(x)
                    self.previous_downloads.append(x.url)

    def check_image(self, item):
        return self.download_images or item.endswith(('.jpg', '.jpeg', '.gif', '.gifv', '.webm', '.png'))

    def check_video(self, item):
        return self.download_videos or item.endswith(('.mp4', '.wmv', '.avi', '.mpg', '.divx'))

    def check_downloaded_content(self, item):
        return not self.avoid_duplicates or item.url not in self.previous_downloads

    def save_unfinished_downloads(self):
        for content in self.content:
            if not content.downloaded:
                self.saved_content[content.url] = [content.user, content.post_title, content.subreddit,
                                                   content.submission_id, content.number_in_seq, content.file_ext]

    def load_unfinished_downloads(self):
        for key, value in self.saved_content.items():
            x = Content(key, value[0], value[1], value[2], value[3], value[4], value[5], self.save_directory,
                        self.subreddit_save_method, self.content_display_only)
            self.content.append(x)
        self.saved_content.clear()

    def set_date_limit(self, last_download_time):
        if self.date_limit is not None and last_download_time > self.date_limit:
            self.date_limit = last_download_time
        elif self.date_limit is None:
            self.date_limit = last_download_time
        if not self.do_not_edit and None is not self.custom_date_limit < last_download_time:
            self.custom_date_limit = None

    def check_save_directory(self):
        SystemUtil.create_directory(self.save_directory)

    def clear_download_session_data(self):
        if Core.Injector.get_settings_manager().save_undownloaded_content:
            self.save_unfinished_downloads()
        self.content.clear()
        self.new_submissions = None
        self.failed_extracts.clear()


class User(RedditObject):

    def __init__(self, version, name, save_path, post_limit, avoid_duplicates, download_videos,
                 download_images, nsfw_filter, name_downloads_by, user_added):
        """
        A subclass of the RedditObject class.  This class is used exclusively to hold users and their information
        """
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, name_downloads_by, user_added)
        self.subreddit_save_method = None
        self.object_type = 'USER'

    @property
    def save_directory(self):
        return '%s%s%s' % (self.save_path, '/' if not self.save_path.endswith('/') else '', self.name)


class Subreddit(RedditObject):

    def __init__(self, version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                 nsfw_filter, subreddit_save_method, name_downloads_by, user_added):
        """
        A subclass of the RedditObject class. This class is used exclusively to hold subreddits and their information.
        Also contains an extra method not used for users to update the subreddit_save_by_method
        """
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, name_downloads_by, user_added)
        self.subreddit_save_method = subreddit_save_method
        self.object_type = 'SUBREDDIT'
