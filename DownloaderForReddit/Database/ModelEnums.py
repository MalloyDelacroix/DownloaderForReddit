from enum import Enum


class DownloadNameMethod(Enum):

    id = 1
    title = 2
    author_name = 3


class SubredditSaveStructure(Enum):

    sub_name = 1
    author_name = 2
    sub_name_author_name = 3
    author_name_sub_name = 4
