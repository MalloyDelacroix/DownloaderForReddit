import os
from unittest import TestCase

from DownloaderForReddit.utils import system_util


class SystemUtilsTests(TestCase):

    path = 'Users/Gorgoth/Downloads/TestSubreddit/Folder9@cool.cats.&&:?12/'

    file_name = 'This is a long title to a post.  This is way longer than any title should be.  I mean, how does ' \
                'someone make a post with a title this long and think that that\'s ok?  How do they sleep at ' \
                'night?  No, this isn\'t a title, its an affront to polite society.  But its out there man, so ' \
                'we\'ll test for it.'

    actual_dir_path = 'Users/Gorgoth/Downloads/TestSubreddit/Folder9@cool#cats#&&##12/This is a long title to a ' \
                      'post#  This is way longer than any title should be#  I mean, how does someone make a post ' \
                      'with a title this long and think that that#s ok#  How'

    actual_lone_file_name = 'This is a long title to a post#  This is way longer than any title should be#  I ' \
                            'mean, how does someone make a post with a title this long and think that that#s ' \
                            'ok#  How...'

    def test_clean_file_name_forbidden_chars(self):
        file_name = 'This :?? is a.....file name'
        self.assertEqual('This ### is a#####file name', system_util.clean(file_name))

    def test_clean_file_name_with_file_separator_characters(self):
        file_name = 'This/is/a/file/name'
        self.assertEqual('This#is#a#file#name', system_util.clean(file_name))

    def test_clean_directory_path(self):
        self.assertEqual(self.actual_dir_path + '...', system_util.clean_path(os.path.join(self.path, self.file_name)))

    def test_clean_sub_directory_path(self):
        sub = 'comments/Test comment'
        actual = self.actual_dir_path + '/' + sub
        self.assertEqual(actual, system_util.clean_path(os.path.join(self.path, self.file_name, sub)))
