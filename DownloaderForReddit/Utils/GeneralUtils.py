import os

from . import Injector
from . import SystemUtil


def rename_invalid_directory(path):
    """
    Renames the supplied invalidated path with the format that is specified in the settings manager.
    :param path: The path that is to be
    :return:
    """
    try:
        if os.path.isdir(path):
            formatting = Injector.get_settings_manager().invalid_rename_format
            new_path = reformat_invalid_name(path, formatting)
            os.rename(path, new_path)
            return True
    except PermissionError:
        return False


def reformat_invalid_name(path, formatting):
    path = path[:-1] if path.endswith(os.sep) or path.endswith('/') else path
    dir_path, dir_name = os.path.split(path)
    new_name = formatting.replace('%[dir_name]', dir_name)
    new_path = SystemUtil.join_path(dir_path, new_name)
    return new_path
