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


logger = logging.getLogger(__name__)


def import_list_from_text_file(file_path):
    """
    Imports a list of reddit objects from the text file at the supplied file path.  Unlike the other importers, this
    method does not make reddit objects from the imported names, but rather only returns a list of names.  It is up to
    the calling method to create the reddit objects.
    :param file_path: The path to the text file that the reddit objects are to be created from.
    :return: A list of names which are to become reddit objects when returned.
    """
    reddit_objects = []
    with open(file_path, 'r') as file:
        content = file.readlines()
    names = [line for line in content]
    for name in names:
        if ',' in name:
            reddit_objects.extend(split_names(name))
        else:
            reddit_objects.append(remove_forbidden_chars(name))
    return reddit_objects if len(reddit_objects) > 0 else None


def split_names(name):
    """Splits the supplied text into multiple names if the text contains a comma."""
    return [remove_forbidden_chars(x) for x in name.split(',') if x != '\n']


def remove_forbidden_chars(name):
    """Removes forbidden characters from the supplied name and returns the new name."""
    return ''.join(x for x in name if x not in (' ', '', '\n'))
