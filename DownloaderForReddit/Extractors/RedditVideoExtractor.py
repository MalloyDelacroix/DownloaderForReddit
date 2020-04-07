"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


from ..Extractors.BaseExtractor import BaseExtractor
from ..Utils import RedditUtils, VideoMerger


class RedditVideoExtractor(BaseExtractor):

    url_key = ['v.redd.it']

    def __init__(self, post, **kwargs):
        super().__init__(post, **kwargs)
        self.post = post
        self.host_vid = self.get_host_vid()
        self.url = None
        self.contains_audio = False
        self.get_vid_url()

    def get_host_vid(self):
        """
        Finds the actual submission that holds the video file to be extracted.  If the post is the original post that
        the video was uploaded to, then None is returned.  If the post is a crosspost from another location,
        the parent crosspost is returned as it is the post which holds the full video information.
        :return: The top level post which holds the video information to be downloaded if the supplied post is a
                 crosspost, otherwise None.
        """
        r = RedditUtils.get_reddit_instance()
        submission = r.submission(id=self.post.reddit_id)
        try:
            return r.submission(submission.crosspost_parrent.split('_')[1])
        except AttributeError:
            return submission

    def get_vid_url(self):
        """
        Extracts the video url from the reddit post and determines if the post is a video and will contain an audio
        file.
        """
        try:
            self.url = self.host_vid.media['reddit_video']['fallback_url']
            self.contains_audio = self.host_vid.is_video
        except AttributeError:
            self.url = self.host_vid.url

    def extract_content(self):
        if self.settings_manager.download_reddit_hosted_videos:
            if self.url is not None:
                video_content = self.get_video_content()
                try:
                    if self.contains_audio:
                        audio_content = self.get_audio_content()
                        if audio_content is not None and video_content is not None:
                            merge_set = VideoMerger.MergeSet(
                                video_id=video_content.full_file_path,
                                audio_id=audio_content.full_file_path,
                                date_modified=self.post.date_posted
                            )
                            VideoMerger.videos_to_merge.append(merge_set)
                except:
                    message = 'Failed to located content'
                    self.handle_failed_extract(message=message, log_exception=True, extractor_error_message=message)
            else:
                message = 'Failed to find acceptable url for download'
                self.handle_failed_extract(message=message, log_exception=True, extractor_error_message=message)

    def get_video_content(self):
        ext = 'mp4'
        content = self.make_content(self.url, ext, name_modifier='(video)')
        return content

    def get_audio_content(self):
        ext = 'mp3'
        index = self.url.rfind('/')
        url = self.url[:index] + '/audio'  # replace end of fallback url to target audio file
        content = self.make_content(url, ext, name_modifier='(audio)')
        return content
