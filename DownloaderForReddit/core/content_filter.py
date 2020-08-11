from sqlalchemy.orm.exc import MultipleResultsFound

from . import const
from ..database.models import Content
from ..utils import injector


class ContentFilter:

    def __init__(self):
        self.settings_manager = injector.get_settings_manager()
        self.db = injector.get_database_handler()
        self.filter_message = 'Passes filter'

    def filter_content(self, post, url, extension):
        dup_passes = self.filter_duplicate(post, url)
        vid_passes = self.filter_reddit_video(post)
        ext_passes = self.filter_file_type(post, extension)
        if not dup_passes:
            self.filter_message = 'Duplicate content'
        if not vid_passes:
            self.filter_message = 'Filtered against reddit video'
        if not ext_passes:
            self.filter_message = f'Filtered against extension {extension}'
        return dup_passes and vid_passes and ext_passes

    def filter_duplicate(self, post, url):
        try:
            if post.significant_reddit_object.avoid_duplicates:
                session = post.get_session()
                return session.query(Content.id).filter(Content.url == url).scalar() is None
            else:
                return True
        except MultipleResultsFound:
            return False

    def filter_reddit_video(self, post):
        return self.settings_manager.download_reddit_hosted_videos or post.domain != 'v.redd.it'

    def filter_file_type(self, post, extension):
        ro = post.significant_reddit_object
        if extension in const.IMAGE_EXT:
            return ro.download_images
        elif extension in const.GIF_EXT:
            return ro.download_gifs
        else:
            return ro.download_videos
