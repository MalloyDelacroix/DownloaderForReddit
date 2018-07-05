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


def export_text(object_list, file_path):
    with open(file_path, 'a') as file:
        for post in object_list:
            file.write(format_post_output(post) + '\n\n')


def format_post_output(post):
    return 'Author: %s\nSubreddit: %s\nTitle: %s\nCreated: %s\nUrl: %s\nStatus: %s\nSave Status: %s' % \
            (post.author, post.subreddit, post.title, post.date_posted, post.url, post.status, post.save_status)
