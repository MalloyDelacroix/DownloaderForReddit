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


import xml.etree.cElementTree as et
from xml.dom import minidom


def export_xml(object_list, file_path):
    root = et.Element('failed_posts')
    for post in object_list:
        make_post_element(root, post)
    xml = minidom.parseString(et.tostring(root)).toprettyxml(indent='    ')
    with open(file_path, 'a') as file:
        file.write(xml)


def make_post_element(parent, post):
    post_element = et.SubElement(parent, 'post')
    et.SubElement(post_element, 'attr', author=post.author)
    et.SubElement(post_element, 'attr', subreddit=post.subreddit)
    et.SubElement(post_element, 'attr', title=post.title)
    et.SubElement(post_element, 'attr', created=post.date_posted)
    et.SubElement(post_element, 'attr', url=post.url)
    et.SubElement(post_element, 'attr', status=post.status)
    et.SubElement(post_element, 'attr', save_status=post.save_status)
