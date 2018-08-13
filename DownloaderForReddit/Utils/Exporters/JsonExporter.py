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


class PostCollection:

    def __init__(self, post_list):
        self.posts = post_list


class JSONPostEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, Post):
            return {'author': o.author,
                    'subreddit': o.subreddit,
                    'title': o.title,
                    'created': o.date_posted,
                    'url': o.url,
                    'status': o.status,
                    'save_status': o.save_status}
        return json.JSONEncoder.default(self, o)


def export_json(object_list, file_path):
    with open(file_path, 'a') as file:
        json.dump(PostCollection(object_list).__dict__, file, cls=JSONPostEncoder, indent=4, ensure_ascii=False)
