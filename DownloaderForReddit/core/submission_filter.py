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

from ..database.model_enums import NsfwFilter, LimitOperator


class SubmissionFilter:

    def filter_submission(self, submission, reddit_object):
        """
        Filters a submission by calling various methods to see if the submission meets the methods criteria based on
        global and reddit object settings and returns True of False depending on if the submission passed all criteria.
        :param submission: A praw submission item that is tested to see if it will be extracted.
        :param reddit_object: The reddit object to which the submission belongs.
        :return: True or False depending on if the submission passed the filter criteria.
        """
        return self.score_filter(submission, reddit_object) and self.nsfw_filter(submission, reddit_object) and \
               self.date_filter(submission, reddit_object)

    def score_filter(self, submission, reddit_object):
        """
        Test the submission to see if it is greater or less than the global settings submission score limit.
        :param submission: A praw submission item to be tested.
        :param reddit_object: The reddit object which the post is being extracted for.
        :return: True if the submissions score limit is meets the global settings criteria, False if it does not.
        """
        if reddit_object.post_score_limit_operator == LimitOperator.NO_LIMIT:
            return True
        elif reddit_object.post_score_limit_operator == LimitOperator.LESS_THAN:
            return submission.score <= reddit_object.post_score_limit
        else:
            return submission.score >= reddit_object.post_score_limit

    def nsfw_filter(self, submission, reddit_object):
        """
        Tests the submission to see if it meets the nsfw criteria set by the supplied reddit object.
        :param submission: A praw submission item to be tested.
        :param reddit_object: The reddit object who's nsfw filter is to be tested against.
        :return: True if the meets the reddit objects nsfw settings criteria, False if it does not.
        """
        if reddit_object.download_nsfw == NsfwFilter.EXCLUDE:
            return not submission.over_18
        elif reddit_object.download_nsfw == NsfwFilter.ONLY:
            return submission.over_18
        else:
            return True

    def date_filter(self, submission, reddit_object):
        """
        Tests the submission date to see if it was submitted after the reddit objects individual date limit setting.
        :param submission: A praw submission item to be tested.
        :param reddit_object: A reddit object (User or Subreddit) which holds the date limit criteria to be tested.
        :return: True if the submission meets the reddit objects date criteria, False if it does not.
        """
        date_limit = self.get_date_limit(reddit_object)
        return submission.created > date_limit.timestamp()

    @staticmethod
    def get_date_limit(reddit_object):
        """
        Returns the reddit objects date_limit or custom_date_limit attribute depending on the what the custom date
        limit is.
        """
        if reddit_object.date_limit is None:
            return reddit_object.absolute_date_limit
        else:
            return reddit_object.date_limit
