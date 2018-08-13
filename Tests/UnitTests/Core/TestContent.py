import unittest
from DownloaderForReddit.Core.Content import Content


class TestContent(unittest.TestCase):

    def make_content(self, subreddit_method):
        self.url = 'http://test-url.com/FluffyKitten.jpg'
        self.user = 'John Everyman'
        self.post_title = 'Fluffiest Kitten Ever'
        self.subreddit = 'Aww'
        self.submission_id = 'FluffyKitten'
        self.number_in_seq = '5'
        self.file_ext = '.jpg'
        self.save_path = 'C:/Users/Gorgoth/Downloads/'
        self.subreddit_save_method = subreddit_method
        self.date_created = '86400'
        self.display_only = False
        self.content = Content(self.url, self.user, self.post_title, self.subreddit, self.submission_id,
                               self.number_in_seq, self.file_ext, self.save_path, self.subreddit_save_method,
                               self.date_created, self.display_only)

    def test_file_name_subreddit_save_method_none(self):
        self.make_content(None)
        self.assertEqual(self.content.filename, '%s%s%s%s' % (self.save_path,
                                                               self.content.clean_filename(self.submission_id),
                                                               self.number_in_seq, self.file_ext))

    def test_file_name_subreddit_save_method_user_name(self):
        self.make_content('User Name')
        correct_file_name = '%s%s/%s%s%s' % (self.save_path, self.user, self.content.clean_filename(self.submission_id),
                                             self.number_in_seq, self.file_ext)
        self.assertEqual(self.content.filename, correct_file_name)

    def test_file_name_subreddit_save_method_subreddit_name(self):
        self.make_content('Subreddit Name')
        correct_file_name = '%s%s/%s%s%s' % (self.save_path, self.subreddit,
                                             self.content.clean_filename(self.submission_id), self.number_in_seq,
                                             self.file_ext)
        self.assertEqual(self.content.filename, correct_file_name)

    def test_file_name_subreddit_save_method_subreddit_name_user_name(self):
        self.make_content('Subreddit Name/User Name')
        correct_file_name = '%s%s/%s/%s%s%s' % (self.save_path, self.subreddit, self.user,
                                                self.content.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
        self.assertEqual(self.content.filename, correct_file_name)

    def test_file_name_subreddit_save_method_user_name_subreddit_name(self):
        self.make_content('User Name/Subreddit Name')
        correct_file_name = '%s%s/%s/%s%s%s' % (self.save_path, self.user, self.subreddit,
                                                self.content.clean_filename(self.submission_id), self.number_in_seq,
                                                self.file_ext)
        self.assertEqual(self.content.filename, correct_file_name)

    def test_file_name_default(self):
        self.make_content('Something Else')
        correct_file_name = '%s%s%s%s' % (self.save_path, self.content.clean_filename(self.submission_id),
                                          self.number_in_seq, self.file_ext)
        self.assertEqual(self.content.filename, correct_file_name)

    def test_clean_file_name(self):
        name_one = 'this is a test of a name that has more than two hundred and thirty characters to see if the clean '\
                   'file name method will correctly limit the size of this name to something shorter that can be ' \
                   'stored on the file system - these are the last few sentences that will put this name over the limit'
        name_two = 'nam/e fo*rbid<d:en char?act..er>s'
        name_three = 'regular name that should be accepted'
        name_one_correct = 'this is a test of a name that has more than two hundred and thirty characters to see if ' \
                           'the clean file name method will correctly limit the size of this name to something...'
        name_two_correct = 'nam#e fo#rbid#d#en char#act##er#s'
        self.assertEqual(Content.clean_filename(name_one), name_one_correct)
        self.assertEqual(Content.clean_filename(name_two), name_two_correct)
        self.assertEqual(Content.clean_filename(name_three), name_three)
