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

from ..Utils import Injector


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
        failed_count = 0
        for ms in videos_to_merge:
            try:
                cmd = 'ffmpeg -i "%s" -i "%s" -c:v copy -c:a aac -strict experimental "%s"' % \
                      (ms.video_path, ms.audio_path, ms.output_path)
                subprocess.call(cmd)
            except:
                failed_count += 1
                logger.error('Failed to merge video', extra={'video_path': ms.video_path, 'audio_path': ms.audio_path,
                                                             'output_path': ms.output_path}, exc_info=True)
        logger.info('Video merger complete', extra={'videos_successfully_merged': len(videos_to_merge) - failed_count,
                                                    'videos_unsuccessfully_merged': failed_count})
        clean_up()
    else:
        logger.warning('Ffmpeg is not installed: unable to merge video and audio files',
                       extra={'videos_to_merge': len(videos_to_merge)})


def clean_up():
    queue = Injector.get_queue()
    for ms in videos_to_merge:
        if os.path.exists(ms.output_path):
            try:
                os.remove(ms.video_path)
                os.remove(ms.audio_path)
            except FileNotFoundError:
                logger.error('Failed to delete reddit video part files', extra={'merged_video_path': ms.output_path},
                             exc_info=True)
            queue.put('Merged reddit video: %s' % ms.output_path)
    videos_to_merge.clear()
