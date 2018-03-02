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


from Extractors.BaseExtractor import BaseExtractor


class RedditUploadsExtractor(BaseExtractor):

    url_key = 'redd.it'

    def __init__(self, url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                 save_path, content_display_only):
        """
        A subclass of the BaseExtractor class.  This class interacts with reddit's own image hosting exclusively.

        At the time of this applications creation this extractor works decently, but is a very fragile extraction method
        and will likely often result in failed extractions. When an inevitable api is made public for this platform,
        this class will be updated to interact with it.
        """
        super().__init__(url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                         save_path, content_display_only)

    def extract_content(self):
        try:
            direct_link = "%s.jpg" % self.url
            self.make_content(direct_link, self.post_title, '.jpg')
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message)
