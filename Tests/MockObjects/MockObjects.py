from datetime import datetime

from DownloaderForReddit.database.models import User, Subreddit, Post, Content
from DownloaderForReddit.database.model_enums import (LimitOperator, PostSortMethod, CommentSortMethod, CommentDownload,
                                                      NsfwFilter)


defaults = {
        'lock_settings': False,
        'post_limit': 25,
        'post_score_limit_operator': LimitOperator.NO_LIMIT,
        'post_score_limit': 1000,
        'avoid_duplicates': True,
        'extract_self_post_links': False,
        'download_self_post_text': False,
        'self_post_file_format': 'txt',
        'comment_file_format': 'txt',
        'download_videos': True,
        'download_images': True,
        'download_gifs': True,
        'download_nsfw': NsfwFilter.INCLUDE,
        'extract_comments': CommentDownload.DO_NOT_DOWNLOAD,
        'download_comments': CommentDownload.DO_NOT_DOWNLOAD,
        'download_comment_content': CommentDownload.DO_NOT_DOWNLOAD,
        'comment_limit': 100,
        'comment_score_limit': 1000,
        'comment_score_limit_operator': LimitOperator.NO_LIMIT,
        'comment_sort_method': CommentSortMethod.NEW,
        'date_limit': None,
        'post_sort_method': PostSortMethod.NEW,
        'post_download_naming_method': '%[title]',
        'comment_naming_method': '%[author_name]-comment',
        'post_save_structure': '%[author_name]',
        'comment_save_structure': '%[post_author_name]/Comments/%[post_title]'
}


def get_user(**kwargs):
    user = User(name=kwargs.pop('name', 'TestUser'), **defaults)
    for key, value in kwargs.items():
        setattr(user, key, value)
    return user


def get_subreddit(**kwargs):
    subreddit = Subreddit(name=kwargs.pop('name', 'TestSubreddit'), **defaults)
    for key, value in kwargs.items():
        setattr(subreddit, key, value)
    return subreddit


def get_post(**kwargs):
    user = kwargs.pop('user', get_user())
    subreddit = kwargs.pop('subreddit', get_subreddit())
    post = Post(
        title=kwargs.pop('title', 'Test Post'),
        date_posted=kwargs.pop('date_posted', datetime.now()),
        domain=kwargs.pop('domain', 'fakesite.com'),
        score=kwargs.pop('score', 2500),
        nsfw=kwargs.pop('nsfw', False),
        reddit_id=kwargs.pop('reddit_id', 'k129r'),
        url=kwargs.pop('url', 'http://www.fakesite.com/id49'),
        is_self=kwargs.pop('is_self', False),
        text=kwargs.pop('text', None),
        text_html=kwargs.pop('text_html', None),
        extracted=kwargs.pop('extracted', False),
        extraction_date=kwargs.pop('extraction_date', None),
        extraction_error=kwargs.pop('extraction_error', None),
        retry_attempts=kwargs.pop('retry_attempts', 0),
        author=kwargs.pop('author', user),
        subreddit=kwargs.pop('subreddit', subreddit),
        significant_reddit_object=kwargs.pop('significant', user),
    )
    session = kwargs.get('session', None)
    if session is not None:
        session.add(post)
    return post


def create_content(**kwargs):
    user = kwargs.pop('user', get_user())
    subreddit = kwargs.pop('subreddit', get_subreddit())
    post = kwargs.pop('post', get_post(user=user, subreddit=subreddit))
    return Content(
        title=kwargs.pop('title', 'Test Content'),
        download_title=kwargs.pop('download_title', 'Test Content'),
        extension=kwargs.pop('extension', 'jpg'),
        url=kwargs.pop('url', 'http://www.fakesite.com/images/42jj6912.jpg'),
        directory_path=kwargs.pop('directory_path', f'C:/Users/Gorgoth/Downloads/RedditDownloads/{user.name}'),
        downloaded=kwargs.pop('downloaded', False),
        download_date=kwargs.pop('download_date', None),
        download_error=kwargs.pop('download_error', None),
        retry_attempts=kwargs.pop('retry_attempts', 0),
        user=kwargs.pop('user', user),
        subreddit=kwargs.pop('subreddit', subreddit),
        post=kwargs.pop('post', post),
        comment=kwargs.pop('comment', None)
    )


def get_unsupported_direct_post(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://invalid_site.com/image/3jfd9nlksd.jpg'
    return post


def get_mock_post_imgur(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://imgur.com/fb2yRj0'
    return post


def get_mock_post_gfycat(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://gfycat.com/KindlyElderlyCony'
    return post


def get_mock_post_gfycat_direct(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://giant.gfycat.com/KindlyElderlyCony.webm'
    return post


def get_mock_post_gfycat_tagged(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://gfycat.com/anchoredenchantedamericanriverotter-saturday-exhausted-weekend-kitten-pissed'
    return post


def get_mock_post_vidble_direct(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://vidble.com/XOwqxH6Xz9.jpg'
    return post


def get_mock_post_vidble(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://vidble.com/XOwqxH6Xz9'
    return post


def get_mock_post_vidible_album(**kwargs):
    post = get_post(**kwargs)
    post.url = 'https://vidble.com/album/3qY9KtlA'
    return post


def get_mock_reddit_video_submission(**kwargs):
    return MockPrawSubmission(
        url=kwargs.get('url', 'https://v.redd.it/lkfmw864od1971'),
        author=kwargs.get('author', 'Gorgoth'),
        title=kwargs.get('title', 'Reddit Video Broh'),
        subreddit=kwargs.get('subreddit', 'PublicFreakout'),
        created=kwargs.get('created', 1521473630.0),
        score=kwargs.get('score', 3500),
        over_18=kwargs.get('nsfw', False),
        is_video=kwargs.get('is_video', False),
        media=kwargs.get('media', None),
        stickied=kwargs.get('stickied', False),
        pinned=kwargs.get('pinned', False)
    )


class MockPrawSubmission:

    def __init__(self, url=None, author=None, title=None, subreddit=None, created=None, score=None, over_18=None,
                 is_video=False, crosspost_parent=None, media=None, stickied=False, pinned=False, _id='abcde'):
        self.url = url
        self.author = author
        self.title = title
        self.subreddit = subreddit
        self.created = created if created is None or isinstance(created, float) else created.timestamp()
        self.score = score
        self.over_18 = over_18
        self.is_video = is_video
        self.crosspost_parent = crosspost_parent
        self.media = media
        self.stickied = stickied
        self.pinned = pinned

        self.id = _id
        self.domain = 'reddit'


class MockPrawSubreddit:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.display_name = self.name
