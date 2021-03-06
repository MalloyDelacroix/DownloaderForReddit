from unittest import TestCase

from DownloaderForReddit import version


class TestVersion(TestCase):

    def test_is_updated_new_version(self):
        against = 'v2.3.7'
        self.assertTrue(version.is_updated('v3.4.8', against))
        self.assertTrue(version.is_updated('v2.5.8', against))
        self.assertTrue(version.is_updated('v2.3.8', against))
        self.assertTrue(version.is_updated('v8.2.0', against))
        self.assertTrue(version.is_updated('v3.4.7', against))
        self.assertTrue(version.is_updated('v3.0.0-beta', against))

    def test_is_updated_old_version(self):
        against = 'v2.3.7'
        self.assertFalse(version.is_updated('v1.4.8', against))
        self.assertFalse(version.is_updated('v2.2.9', against))
        self.assertFalse(version.is_updated('v2.3.6', against))
        self.assertFalse(version.is_updated('v2.3.7', against))
        self.assertFalse(version.is_updated('v0.0.1', against))
        self.assertFalse(version.is_updated('v2.0.0-beta', against))

    def test_update_type(self):
        version.__version__ = 'v2.8.5'
        self.assertEqual(version.update_type('v3.6.5'), 3)
        self.assertEqual(version.update_type('v2.9.8'), 2)
        self.assertEqual(version.update_type('v2.8.7'), 1)
        self.assertEqual(version.update_type('v2.8.5'), 0)
        self.assertEqual(version.update_type('v1.2.3'), 0)
