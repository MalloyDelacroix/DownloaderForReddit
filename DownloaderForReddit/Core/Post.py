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

from urllib.parse import urlparse

from Utils.SystemUtil import epoch_to_str


class Post(object):
    def __init__(self, url, author, title, subreddit, created, status='good', domain=None):
        """
        A class that holds information about a post made on reddit.  This class is used to save post information and
        is also used by the UserFinder.
        :param url: The url that the post links to.
        :param author: The user who made the post to reddit.
        :param title: The title of the post.
        :param subreddit: The subreddit in which the post was made.
        :param created: The epoch time that the post was made.
        :param status: The status of the post.  This is used to hold status information about the post, including the
                       reason the post failed to download if necessary.  Defaults to "good".
        """
        self.url = url
        self.author = author
        self.title = title
        self.subreddit = subreddit
        self.created = created
        self.score = None
        self.domain = domain if domain is not None else self.get_domain()

        self.status = status
        self.save_status = 'Not Saved'

    def __str__(self):
        return self.format_failed_text()

    @property
    def date_posted(self):
        return epoch_to_str(self.created)

    def get_domain(self):
        parsed_url = urlparse(self.url)
        self.domain = '{url.netloc}'.format(url=parsed_url)

    def format_failed_text(self):
        return 'Failed to download content:\nUser: %s  Subreddit: %s  Title: %s\nUrl:  %s\n%s\nSave Status: %s\n' % \
               (self.author, self.subreddit, self.title, self.url, self.status, self.save_status)
