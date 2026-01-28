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
import prawcore
from typing import Generator, Optional

from praw.models import Submission

from ..utils import injector
from ..messaging.message import Message
from . import const


class SearchHandler:
    """
    Handles Reddit search API queries for fetching user submissions
    when direct profile access fails or returns insufficient results.
    """

    def __init__(self, reddit_instance):
        self.logger = logging.getLogger(f'DownloaderForReddit.{__name__}')
        self.reddit = reddit_instance
        self.settings = injector.get_settings_manager()

    def search_user_submissions(
        self,
        username: str,
        limit: Optional[int] = None,
        time_filter: str = 'all'
    ) -> Generator[Submission, None, None]:
        """
        Search for submissions by a specific user across Reddit.

        :param username: The Reddit username to search for
        :param limit: Maximum number of results (None for settings default)
        :param time_filter: Time period to search ('all', 'year', 'month', etc.)
        :return: Generator of praw Submission objects
        """
        if limit is None:
            limit = self.settings.search_fallback_post_limit

        query = f'author:{username}'

        self.logger.info(
            f'Initiating search fallback for user {username}',
            extra={'query': query, 'limit': limit}
        )

        try:
            subreddit = self.reddit.subreddit('all')
            search_results = subreddit.search(
                query,
                sort='new',
                time_filter=time_filter,
                limit=limit
            )

            for submission in search_results:
                # Verify the submission is actually from the target user
                if self.verify_author(submission, username):
                    yield submission

        except prawcore.exceptions.TooManyRequests:
            self.logger.error(
                f'Rate limit reached during search fallback for {username}',
                exc_info=True
            )
            message = (
                f'Reddit rate limit reached during search fallback for: {username}.  '
                f'Please try again shortly.\n'
                f'For more information, please visit the link below:\n{const.RATE_LIMIT_DOC_URL}'
            )
            Message.send_error(message)
            return

        except prawcore.exceptions.RequestException:
            self.logger.error(
                f'Request failed during search fallback for {username}',
                exc_info=True
            )
            Message.send_error(f'Search request failed for {username}')
            return

        except prawcore.exceptions.PrawcoreException as e:
            self.logger.error(
                f'PRAW error during search fallback for {username}: {type(e).__name__}',
                exc_info=True
            )
            Message.send_error(f'Reddit API error during search for {username}')
            return

    def verify_author(self, submission: Submission, expected_username: str) -> bool:
        """
        Verify that a submission is actually from the expected author.

        Reddit search can sometimes return unexpected results. This method
        ensures we only process submissions from the target user.

        :param submission: The praw Submission to verify
        :param expected_username: The username we're searching for
        :return: True if the submission author matches
        """
        try:
            actual_author = submission.author.name.lower()
            return actual_author == expected_username.lower()
        except AttributeError:
            # Author is deleted or inaccessible
            self.logger.debug(
                f'Could not verify author for submission {submission.id}'
            )
            return False

    def should_use_fallback(
        self,
        profile_post_count: int,
        user_setting: Optional[bool],
        global_setting: bool
    ) -> bool:
        """
        Determine if search fallback should be triggered.

        :param profile_post_count: Number of posts retrieved from profile
        :param user_setting: Per-user override (None=use global, True/False=override)
        :param global_setting: Global enable_search_fallback setting
        :return: True if fallback should be used
        """
        # Determine effective setting (per-user overrides global)
        if user_setting is not None:
            use_fallback = user_setting
        else:
            use_fallback = global_setting

        if not use_fallback:
            return False

        threshold = self.settings.search_fallback_threshold

        # Trigger fallback if profile returned fewer posts than threshold
        return profile_post_count < threshold
