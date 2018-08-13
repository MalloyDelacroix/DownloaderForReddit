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

import os


IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')  # TODO: remove gif extensions after gif settings added
GIF_EXT = ('.gif', '.gifv', '.webm')
VID_EXT = ('.mp4', '.wmv', '.avi', '.mpg', '.divx')
ALL_EXT = IMAGE_EXT + GIF_EXT + VID_EXT

SUPPORTED_SITES_FILE = os.path.abspath('Resources/supported_video_sites.txt')
