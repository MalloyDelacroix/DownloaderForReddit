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
import pkgutil

from Core.Post import Post

sys.modules['Post'] = Post

# Imports each extractor module in the Extractor package.  This makes it possible to dynamically search each
# BaseExtractor subclass during operation.
path = pkgutil.extend_path(__path__, __name__)
for importer, name, ispkg in pkgutil.walk_packages(path=path, prefix=__name__ + '.'):
    __import__(name)
