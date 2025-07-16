from unittest import TestCase
from unittest.mock import MagicMock

from DownloaderForReddit.persistence.settings_manager import SettingsManager


class TestSettingsManager(TestCase):

    def setUp(self):
        self.manager = SettingsManager()
        self.manager.load_config_file = MagicMock()  # Mock any file-related operations
        self.manager.save_all = MagicMock()

    def test_ensure_dict_defaults_adds_missing_keys(self):
        loaded_dict = {'a': 1}
        default_dict = {'a': 1, 'b': 2}
        self.manager.ensure_dict_defaults(loaded_dict, default_dict)
        self.assertEqual(loaded_dict['b'], 2)

    def test_ensure_dict_defaults_preserves_existing_keys(self):
        loaded_dict = {'a': 1, 'b': 2}
        default_dict = {'a': 0, 'b': 0}
        self.manager.ensure_dict_defaults(loaded_dict, default_dict)
        self.assertEqual(loaded_dict['a'], 1)
        self.assertEqual(loaded_dict['b'], 2)

    def test_ensure_dict_defaults_recursively_adds_nested_keys(self):
        loaded_dict = {'a': {'x': 1}}
        default_dict = {'a': {'x': 0, 'y': 2}}
        self.manager.ensure_dict_defaults(loaded_dict, default_dict)
        self.assertEqual(loaded_dict['a']['x'], 1)
        self.assertEqual(loaded_dict['a']['y'], 2)

    def test_ensure_dict_defaults_handles_empty_dict(self):
        loaded_dict = {}
        default_dict = {'a': {'x': 0, 'y': 2}}
        self.manager.ensure_dict_defaults(loaded_dict, default_dict)
        self.assertEqual(loaded_dict['a']['x'], 0)
        self.assertEqual(loaded_dict['a']['y'], 2)

    def test_ensure_dict_defaults_empty_default_dict(self):
        loaded_dict = {'a': 1}
        default_dict = {}
        self.manager.ensure_dict_defaults(loaded_dict, default_dict)
        self.assertEqual(loaded_dict, {'a': 1})