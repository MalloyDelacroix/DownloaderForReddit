from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.utils.updater_checker import UpdateChecker
from DownloaderForReddit.utils import injector
from DownloaderForReddit import version


class TestUpdateChecker(TestCase):

    def test_check_notify(self):
        settings = MagicMock()
        injector.settings_manager = settings
        version.__version__ = 'v2.5.8'
        udc = UpdateChecker()

        settings.update_notification_level = 0
        self.assertTrue(udc.check_notify('v2.5.9'))
        self.assertFalse(udc.check_notify('v2.5.8'))

        settings.update_notification_level = 1
        self.assertTrue(udc.check_notify('v2.6.8'))
        self.assertFalse(udc.check_notify('v2.5.9'))

        settings.update_notification_level = 2
        self.assertTrue(udc.check_notify('v3.0.0'))
        self.assertFalse(udc.check_notify('v2.9.9'))
