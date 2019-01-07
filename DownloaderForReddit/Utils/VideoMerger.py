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


import subprocess
import os
import logging
from distutils.spawn import find_executable


logger = logging.getLogger(__name__)

ffmpeg_valid = find_executable('ffmpeg') is not None


# A list of MergeSet's containing the path of the video and audio files that are to be merged.
videos_to_merge = []


class MergeSet:

    def __init__(self, video_path, audio_path, output_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path


def merge_videos():
    if ffmpeg_valid:
        for ms in videos_to_merge:
            try:
                cmd = 'ffmpeg -i "%s" -i "%s" -c:v copy -c:a aac -strict experimental "%s"' % \
                      (ms.video_path, ms.audio_path, ms.output_path)
                subprocess.call(cmd)
                logger.info('Successfully merged %s videos' % len(videos_to_merge))
            except:
                logger.error('Failed to merge videos', extra={'video_path': ms.video_path, 'audio_path': ms.audio_path,
                                                              'output_path': ms.output_path}, exc_info=True)
        clean_up()
    else:
        logger.warning('Ffmpeg is not installed: unable to merge video and audio files',
                       extra={'videos_to_merge': len(videos_to_merge)})


def clean_up():
    for ms in videos_to_merge:
        if os.path.exists(ms.output_path):
            os.remove(ms.video_path)
            os.remove(ms.audio_path)
    videos_to_merge.clear()
