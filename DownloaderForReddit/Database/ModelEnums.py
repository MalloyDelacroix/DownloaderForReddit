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


class CommentDownload(Enum):

    download = 1
    do_not_download = 2
    download_only_author = 3


class NsfwFilter(Enum):

    exclude = -1
    include = 0
    only = 1


class LimitOperator(Enum):

    less_than = -1
    no_limit = 0
    greater_than = 1


class RedditObjectSortMethod(Enum):

    id = 1
    name = 2
    score = 3
    post_count = 4
    content_count = 5
    date_added = 6
    date_created = 7
    last_download = 8
    last_post = 9
