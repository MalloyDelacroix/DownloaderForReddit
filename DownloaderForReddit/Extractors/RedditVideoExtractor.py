
from ..Extractors.BaseExtractor import BaseExtractor
from ..Utils import RedditUtils, VideoMerger


class RedditVideoExtractor(BaseExtractor):

    url_key = ['v.redd.it']

    def __init__(self, post, reddit_object, content_display_only=False):
        super().__init__(post, reddit_object, content_display_only)
        self.post = self.get_host_vid(post)
        self.url = None
        self.contains_audio = False
        self.get_vid_url()

    @staticmethod
    def get_host_vid(post):
        """
        Finds the actual submission that holds the video file to be extracted.  If the post is the original post that
        the video was uploaded to, then the found post is returned.  If the post is a crosspost from another location,
        the parent crosspost is returned as it is the post which holds the full video information.
        :param post: The post which is to be extracted.
        :return: The top level post which holds the video information to be downloaded.
        """
        try:
            return RedditUtils.get_reddit_instance().submission(post.crosspost_parent.split('_')[1])
        except AttributeError:
            return post

    def get_vid_url(self):
        """
        Extracts the video url from the reddit post and determines if the post is a video and will contain an audio
        file.
        """
        try:
            self.url = self.post.media['reddit_video']['fallback_url']
            self.contains_audio = self.post.is_video
        except AttributeError:
            self.url = self.post.url

    def extract_content(self):
        if self.url is not None:
            video_content = self.get_video_content()
            try:
                if self.contains_audio:
                    self.get_audio_content()
                    audio_content = self.get_audio_content()
                    if audio_content is not None and video_content is not None:
                        VideoMerger.videos_to_merge.append(
                            VideoMerger.MergeSet(video_content.filename, audio_content.filename,
                                                 video_content.filename.replace('(video)', '')))
            except:
                message = 'Failed to located content'
                self.handle_failed_extract(message=message, log_exception=True, extractor_error_message=message)
        else:
            message = 'Failed to find acceptable url for download'
            self.handle_failed_extract(message=message, log_exception=True, extractor_error_message=message)

    def get_video_content(self):
        ext = 'mp4'
        return self.make_content(self.url, self.make_name(True), ext)

    def get_audio_content(self):
        ext = 'mp3'
        index = self.url.rfind('/')
        url = self.url[:index] + '/audio'
        return self.make_content(url, self.make_name(False), ext)

    def make_name(self, video_url):
        """
        Makes the appropriate file name based on whether the name is for a video or audio file as well as if the post
        contains an audio file.  If a post contains a video and audio file, they are given the same filename with a
        tag at the end to indicate if the file is the video or audio file.
        :param video_url: True if the name being returned is for a video file, False if it is an audio file.
        :return: The file name to be used in saving the file.
        :type video_url: bool
        """
        if video_url and self.contains_audio:
            return self.get_filename(self.post.id) + '(video)'
        elif self.contains_audio:
            return self.get_filename(self.post.id) + '(audio)'
        else:
            return self.get_filename(self.post.id)
