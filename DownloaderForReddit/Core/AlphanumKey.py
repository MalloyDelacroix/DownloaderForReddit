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

import re


"""
These methods sort a list of alphanumeric values in a human sortable way.  Default sort behaviour is lexicographic.
eg. [thing 9, thing 10, thing 11] as opposed to [thing 10, thing 11, thing 9]
"""


def tryint(s):
    try:
        return int(s)
    except:
        return s


def ALPHANUM_KEY(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]
