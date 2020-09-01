import os

from . import injector
from . import system_util
from .token_parser import TokenParser
from ..gui import message_dialogs


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
