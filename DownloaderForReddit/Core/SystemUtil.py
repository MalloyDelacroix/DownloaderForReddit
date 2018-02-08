import os
import sys
import subprocess


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
            os.mkdir(path)
        except FileExistsError:
            return None
    return None


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
    if sys.platform == 'win32':
        path = os.path.join(os.getenv('APPDATA'), 'SomeGuySoftware', 'DownloaderForReddit')
    else:
        path = 'Data'
    create_directory(path)
    return path
