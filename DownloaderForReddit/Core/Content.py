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
import requests
from PyQt5.QtCore import QRunnable


class Content(QRunnable):

    def __init__(self, url, user, post_title, subreddit, submission_id, number_in_seq, file_ext, save_path,
                 subreddit_save_method):
        """
        Class that holds information about a single file extracted from a reddit submission that is to be downloaded as
        content.  Also holes the method to download the file.

        :param url: The url that the file to be downloaded is located at
        :param user:  The reddit user who submitted to content to reddit
        :param subreddit:  The subreddit the content was submitted to
        :param submission_id:  The content identifier that is to be made part of the file name when the content is saved
                (e.g. the album id if the url is from an imgur album)
        :param number_in_seq:  The number of the file in a sequence of files (e.g. if the file is from an album)
        :param file_ext:  The extension of the file, used to save the file with the correct extension
        """
        super().__init__()
        self.url = url
        self.user = user
        self.post_title = post_title
        self.subreddit = subreddit
        self.submission_id = submission_id
        self.number_in_seq = number_in_seq
        self.file_ext = file_ext
        self.save_path = '%s%s' % (save_path, '/' if not save_path.endswith('/') else '')
        self.subreddit_save_method = subreddit_save_method
        self.output = ''
        self.setAutoDelete(False)
        self.downloaded = False

        self.queue = None

        if self.subreddit_save_method is None:
            self.filename = '%s%s%s%s' % (self.save_path, self.clean_filename(self.submission_id), self.number_in_seq,
                                          self.file_ext)
            self.check_save_path_subreddit(self.save_path)

        elif self.subreddit_save_method == 'User Name':
            self.filename = '%s%s/%s%s%s' % (self.save_path, self.user, self.clean_filename(self.submission_id),
                                             self.number_in_seq, self.file_ext)
            self.check_save_path_subreddit('%s%s/' % (self.save_path, self.user))

        elif self.subreddit_save_method == 'Subreddit Name':
            self.filename = '%s%s/%s%s%s' % (self.save_path, self.subreddit, self.clean_filename(self.submission_id),
                                             self.number_in_seq, self.file_ext)
            self.check_save_path_subreddit('%s%s' % (self.save_path, self.subreddit))

        elif self.subreddit_save_method == 'Subreddit Name/User Name':
            self.filename = '%s%s/%s/%s%s%s' % (self.save_path, self.subreddit, self.user,
                                                self.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
            self.check_save_path_subreddit('%s%s/%s/' % (self.save_path, self.subreddit, self.user))

        elif self.subreddit_save_method == 'User Name/Subreddit Name':
            self.filename = '%s%s/%s/%s%s%s' % (self.save_path, self.user, self.subreddit,
                                                self.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
            self.check_save_path_subreddit('%s%s/%s' % (self.save_path, self.user, self.subreddit))
        else:
            self.filename = '%s%s%s%s' % (self.save_path, self.clean_filename(self.submission_id), self.number_in_seq,
                                          self.file_ext)

    def run(self):
        response = requests.get(self.url, stream=True)
        if response.status_code == 200:
            with open(self.filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            self.queue.put('Saved %s' % self.filename)
            self.downloaded = True
            return None
        self.queue.put('Failed Download:  File %s%s posted by %s failed to download...try link to download '
                       'manually: %s\n' % (self.submission_id, self.number_in_seq, self.user, self.url))

    @staticmethod
    def clean_filename(name):
        """Ensures each file name does not contain forbidden characters and is within the character limit"""
        forbidden_chars = '"*\\/\'.|?:<>'
        filename = ''.join([x if x not in forbidden_chars else '#' for x in name])
        if len(filename) >= 230:
            filename = filename[:225] + '...'
        return filename

    @staticmethod
    def check_save_path_subreddit(path):
        """
        Checks that the supplied directory path is an existing directory and if not, creates the directory.  The try
        except operation is because with multiple numbers of these classes existing at the same time on different
        threads, it is possible that one thread is checking to see that a directory does not exist while another thread
        is creating the directory.  If the first thread then tries to create the directory, it will already exist.
        Multithreading is neat.
        """
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

    def install_queue(self, queue):
        """
        Supplies an instance of the overall queue to every instance of this class so that the main GUI output box
        may be updated with the download progress from this class when it is moved to another thread
        """
        self.queue = queue
