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

from ...Utils.SystemUtil import epoch_to_str


def export_posts_to_xml(post_list, file_path):
    """
    Exports the supplied list of posts to an xml format with each xml element representing one post with all of its
    attributes.
    :param post_list: The list of posts that are to be formatted into an xml file.
    :param file_path: The path at which the xml file will be created.
    """
    root = et.Element('failed_posts')
    for post in post_list:
        make_post_element(root, post)
    xml = minidom.parseString(et.tostring(root)).toprettyxml(indent='    ')
    with open(file_path, 'a') as file:
        file.write(xml)


def make_post_element(parent, post):
    """
    Creates an xml element from the supplied posts attributes.
    :param parent: The parent xml element that the created xml element will be a child of.
    :param post: The post that is to be formatted into an xml element.
    """
    post_element = et.SubElement(parent, 'post')
    et.SubElement(post_element, 'attr', author=post.author)
    et.SubElement(post_element, 'attr', subreddit=post.subreddit)
    et.SubElement(post_element, 'attr', title=post.title)
    et.SubElement(post_element, 'attr', created=post.date_posted)
    et.SubElement(post_element, 'attr', url=post.url)
    et.SubElement(post_element, 'attr', status=post.status)
    et.SubElement(post_element, 'attr', save_status=post.save_status)


def export_reddit_objects_to_xml(object_list, file_path):
    """
    Exports the supplied list of RedditObjects to an xml format with each xml element representing one reddit object
    with all of its relevant and formattable attributes.  Some attributes are omitted from export either due to the
    resulting file size or irrelevancy.
    :param object_list: A list of RedditObjects which are to be exported to an xml file.
    :param file_path: The path at which the xml file will be created.
    """
    root = et.Element('reddit_objects')
    user_root = et.SubElement(root, 'users')
    subreddit_root = et.SubElement(root, 'subreddits')
    for ro in object_list:
        if ro.object_type == 'USER':
            make_reddit_object_element(user_root, ro)
        else:
            make_reddit_object_element(subreddit_root, ro)
    xml = minidom.parseString(et.tostring(root)).toprettyxml(indent='    ')
    with open(file_path, 'a') as file:
        file.write(xml)


def make_reddit_object_element(parent, ro):
    """
    Creates an xml element from the supplied RedditObjects attributes.
    :param parent: The parent xml object that the created xml element will be a child of.
    :param ro: The RedditObject which is to be formatted into an xml element.
    """
    ro_element = et.SubElement(parent, '%s' % ro.object_type.lower())
    et.SubElement(ro_element, 'attr', name=ro.name)
    et.SubElement(ro_element, 'attr', version=ro.version)
    et.SubElement(ro_element, 'attr', save_path=ro.save_path)
    et.SubElement(ro_element, 'attr', post_limit=str(ro.post_limit))
    et.SubElement(ro_element, 'attr', avoid_duplicates=str(ro.avoid_duplicates))
    et.SubElement(ro_element, 'attr', download_videos=str(ro.download_videos))
    et.SubElement(ro_element, 'attr', download_images=str(ro.download_images))
    et.SubElement(ro_element, 'attr', nsfw_filter=ro.nsfw_filter)
    et.SubElement(ro_element, 'attr', added_on=epoch_to_str(ro.user_added))
    et.SubElement(ro_element, 'attr', do_not_edit=str(ro.do_not_edit))
    et.SubElement(ro_element, 'attr', save_undownloaded_content=str(ro.save_undownloaded_content))
    et.SubElement(ro_element, 'attr', download_enabled=str(ro.enable_download))
