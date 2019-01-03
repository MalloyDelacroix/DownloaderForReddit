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
import logging

from ...Core.RedditObjects import User, Subreddit


logger = logging.getLogger(__name__)


def import_list_from_xml(file_path):
    """
    Imports a list of reddit objects from the xml file at the supplied file path.
    :param file_path: The path to the xml file from which to build the user list.
    :return: A list of RedditObjects built from the supplied xml file.
    """
    reddit_objects = []
    tree = et.parse(file_path)
    root = tree.getroot()
    for sub_element in root:
        for child in sub_element:
            ro = make_reddit_object(child)
            if ro is not None:
                reddit_objects.append(ro)
    logger.info('Imported from file', extra={'import_count': len(reddit_objects)})
    return reddit_objects if len(reddit_objects) > 0 else None


def make_reddit_object(element):
    """
    Creates a User or Subreddit object, depending on the supplied elements tag, with the attributes imported from the
    supplied xml element.
    :param element: The element that the reddit object is to be built from.
    :return: A RedditObject build from the attributes of the supplied element.
    """
    try:
        name = element.find('name').text
        version = element.find('version').text
        save_path = element.find('save_path').text
        post_limit = int(element.find('post_limit').text)
        avoid_duplicates = bool(element.find('avoid_duplicates').text)
        download_videos = bool(element.find('download_videos').text)
        download_images = bool(element.find('download_images').text)
        nsfw_filter = element.find('nsfw_filter').text
        name_downloads_by = element.find('name_downloads_by').text
        subreddit_save_method = element.find('subreddit_save_method').text
        date_limit = float(element.find('date_limit').attrib['epoch'])
        custom_date_limit = element.find('custom_date_limit').attrib['epoch']
        added_on = float(element.find('added_on').attrib['epoch'])
        do_not_edit = bool(element.find('do_not_edit').text)
        save_undownloaded_content = bool(element.find('save_undownloaded_content').text)
        download_enabled = bool(element.find('download_enabled').text)
        if element.tag == 'user':
            reddit_object = User(version, name, save_path, post_limit, avoid_duplicates, download_videos,
                                 download_images, nsfw_filter, name_downloads_by, added_on)
        else:
            reddit_object = Subreddit(version, name, save_path, post_limit, avoid_duplicates, download_videos,
                                      download_images, nsfw_filter, subreddit_save_method, name_downloads_by, added_on)
        reddit_object.date_limit = date_limit
        reddit_object.custom_date_limit = float(custom_date_limit) if custom_date_limit != 'None' else None
        reddit_object.do_not_edit = do_not_edit
        reddit_object.save_undownloaded_content = save_undownloaded_content
        reddit_object.download_enabled = download_enabled
        return reddit_object
    except:
        logger.warning('Failed to import reddit object from xml element', exc_info=True)
        return None
