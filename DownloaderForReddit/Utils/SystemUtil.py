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

import os
import sys
import subprocess
import shutil
import datetime


def open_in_system(item):
    """
    Opens the supplied file system item in the default system manner.  The supplied item must be a full path to a file
    system item that has a default open method.
    :param item: A full path to a file system item that can be opened.
    :type item: str
    """
    if sys.platform == 'win32':
        os.startfile(item)
    else:
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([opener, item])


def create_directory(path):
    """
    Checks to see if the supplied directory path exists and creates the directory if it does not.  Also handles a
    FileExistsException which happens sometimes when multiple content items are being simultaneously downloaded and
    both threads try to create the same directory at the same time.
    :param path: The path of the directory that is checked and created.
    :type path: str
    :return: None if the path already exists
    """
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass


def rename_directory_deleted(path):
    """
    Renames a folder with the '(deleted)' after the folder name.
    :param path: The path of the folder that is to be renamed with the "(deleted)" marker
    :type path: str
    :return: True if the rename was successful and False if not.
    :rtype: bool
    """
    try:
        if os.path.isdir(path):
            path = path[:-1] if path.endswith(os.sep) or path.endswith('/') else path
            os.rename(path, '%s (deleted)' % path)
        return True
    except PermissionError:
        return False


def set_file_modify_time(file, epoch):
    """
    Sets a files date modified metadata to the time in the supplied epoch time.
    :param file: The file who's date modified time is to be changed.
    :param epoch: The datetime in seconds of the new modified date.
    :type file: str
    :type epoch: int
    :return: True if the modification was successful, False if it was not.
    :rtype: bool
    """
    os.utime(file, times=(epoch, epoch))


def get_data_directory():
    """
    Builds and returns a path the DownloaderForReddit data files location based on the users OS.  This will either be
    in the AppData directory if using Windows, or a sub-directory directory named 'Data' in the applications directory
    if using Linux.
    :return: The path to the DownloaderForReddit data directory for the users system.
    :rtype: str
    """
    data_dir = os.path.join('SomeGuySoftware', 'DownloaderForReddit')
    if sys.platform == 'win32':
        path = os.path.join(os.getenv('APPDATA'), data_dir)
    elif sys.platform.startswith('linux'):
        path = os.path.join(os.path.expanduser('~'), '.%s' % data_dir)
    elif sys.platform == 'darwin':
        path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', data_dir)
    else:
        path = 'Data'
    create_directory(path)
    return path


def import_data_file(directory, file):
    """
    Attempts to move the supplied file from the supplied directory into the applications data directory.  If this fails
    because of an OSError, this likely means the file is located on an external drive, in which case the file is copied
    from the source folder to the data folder.
    :param directory: The directory that the file is currently located in.
    :param file: The file that is to be imported.
    :type directory: str
    :type file: str
    """
    source = os.path.join(directory, file)
    dest = os.path.join(get_data_directory(), file)
    try:
        os.rename(source, dest)
    except OSError:
        shutil.copy(source, dest)


def epoch_to_str(epoch_time):
    if type(epoch_time) == int or type(epoch_time) == float:
        return datetime.datetime.fromtimestamp(epoch_time).strftime('%m/%d/%Y %I:%M %p')
    else:
        return None


def delete_file(file_path):
    """
    Deletes the file at the supplied file path.
    :param file_path: The path of the file to be deleted.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
