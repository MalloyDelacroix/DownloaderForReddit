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


from Core import Injector


class PostFilter:

    def __init__(self):
        self.settings_manager = Injector.get_settings_manager()

    def filter_post(self, post, reddit_object):
        """
        Filters a post by calling various methods to see if the post meets the methods criteria based on global and
        reddit object settings and returns True of False depending on if the post passed all criteria.
        :param post: A praw submission item that is tested to see if it will be extracted.
        :param reddit_object: The reddit object to which the post belongs.
        :return: True or False depending on if the post passed the filter criteria.
        """
        return self.score_filter(post) and self.nsfw_filter(post, reddit_object) and \
               self.date_filter(post, reddit_object)

    def score_filter(self, post):
        """
        Test the post to see if it is greater or less than the global settings post score limit.
        :param post: A praw submission item to be tested.
        :return: True if the posts score limit is meets the global settings criteria, False if it does not.
        """
        if self.settings_manager.restrict_by_score:
            if self.settings_manager.score_limit_operator == 'GREATER':
                return post.score >= self.settings_manager.post_score_limit
            else:
                return post.score <= self.settings_manager.post_score_limit
        else:
            return True

    def nsfw_filter(self, post, reddit_object):
        """
        Tests the post to see if it meets the nsfw criteria set by the supplied reddit object.
        :param post: A praw submission item to be tested.
        :param reddit_object: The reddit object who's nsfw filter is to be tested against.
        :return: True if the meets the reddit objects nsfw settings criteria, False if it does not.
        """
        if reddit_object.nsfw_filter == 'EXCLUDE':
            return not post.over_18
        elif reddit_object.nsfw_filter == 'ONLY':
            return post.over_18
        else:
            return True

    def date_filter(self, post, reddit_object):
        """
        Tests the post date to see if it was posted after the reddit objects individual date limit setting.
        :param post: A praw submission item to be tested.
        :param reddit_object: A reddit object (User or Subreddit) which holds the date limit criteria to be tested.
        :return: True if the post meets the reddit objects date criteria, False if it does not.
        """
        date_limit = self.get_date_limit(reddit_object)
        return post.created > date_limit

    @staticmethod
    def get_date_limit(reddit_object):
        """
        Returns the reddit objects date_limit or custom_date_limit attribute depending on the what the custom date
        limit is.
        """
        if reddit_object.custom_date_limit is None:
            return reddit_object.date_limit
        else:
            return reddit_object.custom_date_limit
