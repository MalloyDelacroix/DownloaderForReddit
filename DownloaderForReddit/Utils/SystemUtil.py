import os
import sys
import subprocess
import shutil
import time


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


def get_epoch(time_string):
    """
    This method is deprecated for use with QDateTimeWidgets.  Use QDateTimeWidget.dateTime().toSecsSinceEpoch()

    Returns the epoch time for a date/time string and handles appropriately in the rare case that time is formatted
    incorrectly.
    :param time_string: The time string for which an epoch is requested.
    :type time_string: str
    :return: A time in seconds since the epoch.
    :rtype: int
    """
    try:
        return get_time_int(time_string)
    except ValueError:
        if time_string.endswith('p. m.'):
            time_string = time_string.replace('p. m.', 'pm')
        elif time_string.endswith('a. m.'):
            time_string = time_string.replace('a. m.', 'am')
        return get_time_int(time_string)


def get_time_int(time_string):
    return int(time.mktime(time.strptime(time_string, '%m/%d/%Y %I:%M %p')))
