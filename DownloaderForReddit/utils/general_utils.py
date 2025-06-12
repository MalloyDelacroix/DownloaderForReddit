import os
import logging
from datetime import datetime, date

from . import injector
from . import system_util
from .token_parser import TokenParser
from ..gui import message_dialogs


logger = logging.getLogger(__name__)


def rename_invalid_directory(path):
    """
    Renames the supplied invalidated path with the format that is specified in the settings manager.
    :param path: The path that is to be
    :return:
    """
    try:
        if os.path.isdir(path):
            formatting = injector.get_settings_manager().invalid_rename_format
            new_path = reformat_invalid_name(path, formatting)
            os.rename(path, new_path)
            return True
    except PermissionError:
        return False


def reformat_invalid_name(path, formatting):
    path = path[:-1] if path.endswith(os.sep) or path.endswith('/') else path
    dir_path, dir_name = os.path.split(path)
    new_name = formatting.replace('%[dir_name]', dir_name)
    new_path = system_util.join_path(dir_path, new_name)
    return new_path


def get_reddit_object_download_folder(reddit_object):
    sub_path = TokenParser.parse_tokens(reddit_object, reddit_object.post_save_structure)
    if reddit_object.object_type == 'USER':
        base_path = injector.get_settings_manager().user_save_directory
    else:
        base_path = injector.get_settings_manager().subreddit_save_directory
    return os.path.join(base_path, sub_path)


def open_reddit_object_download_folder(reddit_object, calling_window):
    try:
        path = get_reddit_object_download_folder(reddit_object)
        system_util.open_in_system(path)
    except FileNotFoundError:
        message_dialogs.no_download_folder(calling_window, reddit_object.object_type.lower())


def open_post_in_browser(post):
    try:
        url = post.url
        system_util.open_in_system(url)
    except Exception as e:
        print(e)


def ensure_content_download_path(content):
    """
    Checks the content's full file path to make sure there are no naming conflicts.  If there are, a number is
    incremented and appended to the contents title until a naming conflict no longer exists.
    :param content: The Content item who's path is to be checked.
    """
    try:
        system_util.create_directory(content.directory_path)
    except PermissionError:
        logger.error('Could not create directory path', extra={'directory_path': content.directory_path}, exc_info=True)
    unique_count = 1
    clean_title = system_util.clean(content.title)
    download_title = clean_title
    path = content.get_full_file_path(download_title)
    while os.path.exists(path):
        download_title = f'{clean_title}({unique_count})'
        path = content.get_full_file_path(download_title)
        unique_count += 1
    return download_title


def ensure_file_path(file_path: str) -> str:
    """
    Checks the supplied file path to make sure there are no naming conflicts.  If there are, a number is incremented
    and appended after the file name portion until a naming conflict no longer exists.  The file path is returned.  If
    the directory does not exist, it is created.  If there is a permission error, the error is logged and the operation
    continues.
    :param file_path: The file path to check for naming conflicts.
    :return: A clean, unique file path to an existing directory.
    """
    base_path, title, ext = split_file_path(file_path)
    try:
        system_util.create_directory(base_path)
    except PermissionError:
        logger.error('Could not create directory path', extra={'directory_path': base_path}, exc_info=True)
    unique_count = 1
    clean_title = system_util.clean_path(title)
    path = system_util.join_path(base_path, f'{clean_title}{ext}')
    while os.path.exists(path):
        title = f'{clean_title}({unique_count}){ext}'
        path = system_util.join_path(base_path, title)
        unique_count += 1
    return path


def split_file_path(file_path: str) -> tuple[str, str, str]:
    """
    Splits a supplied file path into three parts: the base path, the title, and the extension.  All three are returned
    as a tuple.
    :param file_path: The file path to split.
    :return: A tuple containing the base path, the title, and the extension of the supplied file path.
    """
    base_path = os.path.dirname(file_path)
    raw_title = os.path.basename(file_path)
    title, ext = os.path.splitext(raw_title)
    return base_path, title, ext


def format_datetime(date_time: datetime):
    settings_manager = injector.get_settings_manager()
    datetime_format = settings_manager.datetime_display_format
    return date_time.strftime(datetime_format)


def format_date(raw_date: date):
    settings_manager = injector.get_settings_manager()
    date_format = settings_manager.date_display_format
    return raw_date.strftime(date_format)


def format_date_path(formatted_date):
    """
    Takes a formatted date string, and returns a version that can be used in a file path (ie: the slashes are replaced
    with dashes and forbidden characters are removed.)
    :param formatted_date: A formatted date string.
    :return: The supplied formatted date string in a format that can be used for file paths.
    """
    return formatted_date.replace('/', '-').replace('\\', '-').replace(':', '--')


def format_raw_datetime(date_time, format_str):
    return date_time.strftime(format_str)
