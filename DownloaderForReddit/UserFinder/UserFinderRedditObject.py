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


from Core.RedditObjects import Subreddit, User


class UserFinderUser(User):

    """
    A subclass of the User class used to hold information about a user for use by the UserFinder
    """

    def __init__(self, karma, user_since, version, name, save_path, post_limit, avoid_duplicates, download_videos,
                 download_images, nsfw_filter, name_downloads_by, user_added):
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, name_downloads_by, user_added)
        self.total_karma = karma
        self.user_since = user_since
        self.last_post_date = None
        self.post_count = None

    @property
    def save_directory(self):
        """
        Overrides the super User class's save directory property to provide a text item that is not used but also does
        not cause exceptions in other parts of the program that need a text path here.
        :return: A mock path string
        :rtype: str
        """
        return 'path/'


class UserFinderSubreddit(Subreddit):

    """
    A subclass of the Subreddit class used to hold information about a subreddit for use by the UserFinder
    """

    def __init__(self, version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                 nsfw_filter, subreddit_save_method, name_downloads_by, user_added):
        super().__init__(version, name, save_path, post_limit, avoid_duplicates, download_videos, download_images,
                         nsfw_filter, subreddit_save_method, name_downloads_by, user_added)
        self.extracted_post_dict = {}

    def consolidate_posts(self):
        """
        Combs through posts in the new submissions list for posts that may have the same author, and if found
        consolidates the posts to the extracted_post_dict under the key of the authors name for easier use.
        """
        for post in self.new_submissions:
            if post.author.name in self.extracted_post_dict:
                self.extracted_post_dict[post.author.name].append(post)
            else:
                self.extracted_post_dict[post.author.name] = [post]
