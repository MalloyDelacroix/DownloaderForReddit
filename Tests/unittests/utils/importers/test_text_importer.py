from unittest import TestCase

from DownloaderForReddit.utils.importers import text_importer


class TestTextImporter(TestCase):

    def test_remove_forbidden_chars(self):
        text = ' this \n is a\nname-for-import  '
        clean = text_importer.remove_forbidden_chars(text)
        self.assertEqual('thisisaname-for-import', clean)

    def test_split_names(self):
        names = 'name_one, name_two, name_three, name_four'
        names = text_importer.split_names(names)
        self.assertEqual(['name_one', 'name_two', 'name_three', 'name_four'], names)

    def test_split_names_with_extra_commas(self):
        names = ', name_one, name_two, name_three, name_four, '
        names = text_importer.split_names(names)
        self.assertEqual(['name_one', 'name_two', 'name_three', 'name_four'], names)

    def test_filter_import_list(self):
        names = ['one', 'two', 'one', 'three', 'One', 'ONE', 'oNe', 'four', 'one', '', 'five', 'one', 'ONE', 'six']
        filtered_names = text_importer.filter_import_list(names)
        correct_names = ['one', 'two', 'three', 'four', 'five', 'six']
        self.assertEqual(correct_names, filtered_names)
