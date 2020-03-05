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

import json
import logging

from ...Database.Models import Post, RedditObject
from ...Utils.SystemUtil import epoch_to_str


logger = logging.getLogger(__name__)


class PostCollection:

    def __init__(self, post_list):
        self.posts = post_list


class JSONPostEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Post):
            return {
                'author': o.author,
                'subreddit': o.subreddit,
                'title': o.title,
                'score': o.score,
                'reddit_id': o.reddit_id,
                'created': o.date_posted,
                'url': o.url,
                'extracted': o.extracted,
                'extraction_date': o.extraction_date,
                'extraction_error': o.extraction_error,
                'download_session_id': o.download_session_id
            }
        return json.JSONEncoder.default(self, o)


class RedditObjectCollection:

    def __init__(self, object_list):
        self.object_list = object_list


class JSONRedditObjectEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, RedditObject):
            return {
                'name': o.name,
                'object_type': o.object_type,
                'post_limit': o.post_limit,
                'avoid_duplicates': o.avoid_duplicates,
                'download_videos': o.download_videos,
                'download_images': o.download_images,
                'download_comments': o.download_comments,
                'download_comment_content': o.download_comment_content,
                'download_nsfw': o.download_nsfw,
                'download_naming_method': o.download_naming_method,
                'subreddit_save_structure': o.subreddit_save_structure,
                'absolute_date_limit_epoch': o.absolute_date_limit,
                'absolute_date_limit_readable': epoch_to_str(o.absolute_date_limit),
                'date_limit_epoch': o.date_limit,
                'date_limit_readable': epoch_to_str(o.date_limit) if o.date_limit is not None else None,
                'date_added_epoch': o.date_added,
                'date_added_readable': epoch_to_str(o.date_added),
                'lock_settings': o.lock_settings,
                'download_enabled': o.download_enabled,
                'post_sort_method': o.post_sort_method,
                'new': o.new,
                'significant': o.significant,
                'active': o.active,
                'inactive_date': o.inactive_date
            }


def export_posts_to_json(post_list, file_path):
    """
    Exports the posts in the supplied post_list to a formatted json file.
    :param post_list: A list of posts which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    """
    with open(file_path, mode='a', encoding='utf-8') as file:
        json.dump(PostCollection(post_list).__dict__, file, cls=JSONPostEncoder, indent=4, ensure_ascii=False)
    logger.info('Exported post list to json file', extra={'export_count': len(post_list)})


def export_reddit_objects_to_json(object_list, file_path):
    """
    Exports the reddit objects in the supplied object_list to a formatted json file.
    :param object_list: A list of RedditObjects which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    """
    with open(file_path, 'a', encoding='utf-8') as file:
        json.dump(RedditObjectCollection(object_list).__dict__, file, cls=JSONRedditObjectEncoder, indent=4,
                  ensure_ascii=False)
    logger.info('Exported reddit object list to json file', extra={'export_count': len(object_list)})
