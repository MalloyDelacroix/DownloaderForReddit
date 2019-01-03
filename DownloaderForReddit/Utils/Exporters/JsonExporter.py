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

from ...Core.Post import Post
from ...Core.RedditObjects import RedditObject
from ...Utils.SystemUtil import epoch_to_str


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
                'created': o.date_posted,
                'url': o.url,
                'status': o.status,
                'save_status': o.save_status
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
                'version': o.version,
                'save_path': o.save_path,
                'post_limit': o.post_limit,
                'avoid_duplicates': o.avoid_duplicates,
                'download_videos': o.download_videos,
                'download_images': o.download_images,
                'nsfw_filter': o.nsfw_filter,
                'name_downloads_by': o.name_downloads_by,
                'subreddit_save_method': o.subreddit_save_method,
                'date_limit_epoch': o.date_limit,
                'date_limit_readable': epoch_to_str(o.date_limit),
                'custom_date_limit_epoch': o.custom_date_limit,
                'custom_date_limit_readable': epoch_to_str(o.custom_date_limit) if o.custom_date_limit is not None else
                None,
                'added_on_epoch': o.user_added,
                'added_on_readable': epoch_to_str(o.user_added),
                'do_not_edit': o.do_not_edit,
                'save_undownloaded_content': o.save_undownloaded_content,
                'download_enabled': o.enable_download
            }


def export_posts_to_json(post_list, file_path):
    """
    Exports the posts in the supplied post_list to a formatted json file.
    :param post_list: A list of posts which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    """
    with open(file_path, 'a') as file:
        json.dump(PostCollection(post_list).__dict__, file, cls=JSONPostEncoder, indent=4, ensure_ascii=False)


def export_reddit_objects_to_json(object_list, file_path):
    """
    Exports the reddit objects in the supplied object_list to a formatted json file.
    :param object_list: A list of RedditObjects which are to be exported to a json file.
    :param file_path: The path at which the json file will be created.
    """
    with open(file_path, 'a') as file:
        json.dump(RedditObjectCollection(object_list).__dict__, file, cls=JSONRedditObjectEncoder, indent=4,
                  ensure_ascii=False)
