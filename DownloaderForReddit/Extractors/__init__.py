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


import sys

from Core.Post import Post

# Import each extractor class in the Extractors package so that BaseExtractor.__subclasses__() will pick up the
# extractor class to be used in the Extractor.assign_extractor method.
from Extractors.ImgurExtractor import ImgurExtractor
from Extractors.GfycatExtractor import GfycatExtractor
from Extractors.VidbleExtractor import VidbleExtractor
from Extractors.RedditUploadsExtractor import RedditUploadsExtractor


sys.modules['Post'] = Post
