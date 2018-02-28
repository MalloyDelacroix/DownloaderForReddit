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


from bs4 import BeautifulSoup

from Extractors.BaseExtractor import BaseExtractor


class VidbleExtractor(BaseExtractor):

    def __init__(self, url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                 save_path, content_display_only):
        """
        A sublcass of the BaseExtractor class.  This class interacts exclusively with the Vidble website via BeautifulSoup4
        """
        super().__init__(url, user, post_title, subreddit, creation_date, subreddit_save_method, name_downloads_by,
                         save_path, content_display_only)
        self.vidble_base = "https://vidble.com"

    def extract_content(self):
        """Dictates which extraction method should be used"""
        try:
            if '/show/' in self.url or '/explore/' in self.url:
                self.extract_single()
            elif '/album/' in self.url:
                self.extract_album()
            elif self.url.lower().endswith(('.jpg', 'jpeg', '.png', '.gif', '.gifv', '.mp4', 'webm')):
                self.extract_direct_link()
            else:
                self.extract_album()  # If it hasn't found a match by here, try for album and hope it works
        except:
            message = 'Failed to locate content'
            self.handle_failed_extract(message=message, extractor_error_message=message)

    def extract_single(self):
        domain, vidble_id = self.url.rsplit('/', 1)
        if '.' in vidble_id:
            vidble_id = vidble_id[:vidble_id.rfind('.')]
        soup = BeautifulSoup(self.get_text(self.url), 'html.parser')
        imgs = soup.find_all('img')
        for img in imgs:
            img_class = img.get('class')
            if img_class is not None and img_class[0] == 'img2':
                link = img.get('src')
                if link is not None:
                    base, extension = link.rsplit('.', 1)
                    file_name = self.post_title if self.name_downloads_by == 'Post Title' else vidble_id
                    self.make_content(self.vidble_base + link, file_name, extension)

    def extract_album(self):
        count = 1
        domain, vidble_id = self.url.rsplit('/', 1)
        soup = BeautifulSoup(self.get_text(self.url), 'html.parser')
        imgs = soup.find_all('img')
        for img in imgs:
            img_class = img.get('class')
            if img_class is not None and img_class[0] == 'img2':
                link = img.get('src')
                if link is not None:
                    base, extension = link.rsplit('.', 1)
                    file_name = self.post_title if self.name_downloads_by == 'Post Title' else vidble_id
                    self.make_content(self.vidble_base + link, file_name, extension, count)
                    count += 1

    def extract_direct_link(self):
        domain, id_with_ext = self.url.rsplit('/', 1)
        vidble_id, extension = id_with_ext.rsplit('.', 1)
        file_name = self.post_title if self.name_downloads_by == 'Post Title' else vidble_id
        self.make_content(self.url, file_name, extension)
