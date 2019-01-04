
from ..Extractors.BaseExtractor import BaseExtractor
from ..Utils import RedditUtils


class RedditVideoExtractor(BaseExtractor):

    url_key = ['v.redd.it']

    def __init__(self, post, reddit_object, content_display_only=False):
        super().__init__(post, reddit_object, content_display_only)
        self.post = self.get_host_vid(post)

    @staticmethod
    def get_host_vid(post):
        """
        Finds the actual submission that holds the video file to be extracted.  If the post is the original post that
        the video was uploaded to, then the found post is returned.  If the post is a crosspost from another location,
        the parent crosspost is returned as it is the post which holds the full video information.
        :param post: The post which is to be extracted.
        :return: The top level post which holds the video information to be downloaded.
        """
        if post.is_crosspost:
            return RedditUtils.get_reddit_instance().submission(post.crosspost_parent.split('_')[1])
        else:
            return post

    def extract_content(self):
        try:
            if self.post.is_video:
                vid_url = self.get_video_url()
                audio_url = self.get_audio_url()
        except:
            message = 'Failed to located content'
            self.handle_failed_extract(message=message, log_exception=True, extractor_error_message=message)

    def get_video_url(self):
        pass

    def get_audio_url(self):
        pass
