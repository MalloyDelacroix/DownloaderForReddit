import enum


class DownloadNameMethod(enum):

    id = 1
    title = 2
    author_name = 3


class SubredditSaveStructure(enum):

    sub_name = 1
    author_name = 2
    sub_name_author_name = 3
    author_name_sub_name = 4
