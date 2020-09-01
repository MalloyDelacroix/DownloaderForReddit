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

import praw
import prawcore
import logging
from datetime import datetime
from collections import namedtuple

from ..version import __version__


logger = logging.getLogger('DownloaderForReddit.{}'.format(__name__))
ValidationSet = namedtuple('ValidationSet', 'name date_created valid')


def get_reddit_instance():
    reddit_instance = praw.Reddit(user_agent='python:DownloaderForReddit:%s (by /u/MalloyDelacroix)' % __version__,
                                  client_id='frGEUVAuHGL2PQ', client_secret=None)
    return reddit_instance


def get_post_author_name(praw_post):
    """
    Handles an exception thrown in the event that a post retrieved from reddit does not have an author attribute.
    """
    try:
        return praw_post.author.name
    except AttributeError:
        return 'Unable to find author name'


def get_post_sub_name(praw_post):
    """
    Handles an exception thrown in the event that a post retrieved from reddit does not have a subreddit attribute.
    """
    try:
        return praw_post.subreddit.display_name
    except AttributeError:
        return 'Unable to find subreddit name'


class NameChecker:

    """
    This class is to check for the existence of a reddit object name using praw, then report back whether the name
    exists or not.  This class is intended to be ran in a separate thread.
    """

    def __init__(self, object_type):
        """
        Initializes the NameChecker and establishes its operation setup regarding whether to target users or subreddits.
        :param object_type: The type of reddit object (USER or SUBREDDIT) that the supplied names will be.
        :type object_type: str, None
        """
        super().__init__()
        self.logger = logging.getLogger('DownloaderForReddit.%s' % __name__)
        self.r = get_reddit_instance()
        self.continue_run = True
        self.object_type = object_type

    def check_reddit_object_name(self, name):
        if self.object_type == 'USER':
            return self.check_user_name(name)
        else:
            return self.check_subreddit_name(name)

    def check_user_name(self, name):
        user = self.r.redditor(name)
        try:
            # actual name pulled from reddit because capitalization differences may cause problems throughout the app.
            # Creation date is checked first because praw objects are evaluated lazily, and calling user.name first will
            # not send anything to the server and will only return the name as it was supplied.  By getting the creation
            # date first, the redditor object is updated with information supplied by reddit's server.
            created = datetime.fromtimestamp(user.created)
            actual_name = user.name
            return ValidationSet(name=actual_name, date_created=created, valid=True)
        except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect, AttributeError):
            return ValidationSet(name=name, date_created=None, valid=False)
        except:
            self.logger.error('Unable to validate user name', extra={'user_name': name}, exc_info=True)
            return ValidationSet(name=name, date_created=None, valid=False)

    def check_subreddit_name(self, name):
        sub = self.r.subreddit(name)
        try:
            # actual name pulled from reddit because capitalization differences may cause problems throughout the app
            created = datetime.fromtimestamp(sub.created)
            actual_name = sub.display_name
            return ValidationSet(name=actual_name, date_created=created, valid=True)
        except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect, AttributeError):
            return ValidationSet(name=name, date_created=None, valid=False)
        except:
            self.logger.error('Unable to validate subreddit name', extra={'subreddit_name': name}, exc_info=True)
            return ValidationSet(name=name, date_created=None, valid=False)
