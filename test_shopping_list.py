import unittest
import sys
from unittest.mock import MagicMock, patch, mock_open
sys.modules['config'] = MagicMock()
from shopping_list import ShoppingList



class TestShoppingList(unittest.TestCase):
    def setUp(self):
        # Mock logger
        self.mock_logger = MagicMock()

    @patch("shopping_list.config")
    @patch("shopping_list.open", new_callable=mock_open, read_data='{"StarSystem": "TestSystem", "DeliveryStation": "TestStation", "Materials": {"Item1": 10}}')
    def test_load_from_journal_success(self, mock_open, mock_config):
        # Mock config to provide journaldir
        mock_config.get_str.return_value = "/mock/journal/dir"
        mock_config.default_journal_dir = "/mock/default/dir"

        shopping_list = ShoppingList(self.mock_logger)
        shopping_list.load_from_journal()

        # Assertions
        self.mock_logger.info.assert_any_call("Loading shopping list from journal")
        self.mock_logger.info.assert_any_call("Loaded shopping list from /mock/journal/dir/Colonisation.json")
        self.assertEqual(shopping_list.target_system, "TestSystem")
        self.assertEqual(shopping_list.target_station, "TestStation")
        self.assertEqual(shopping_list.shopping_list, {"Item1": 10})

    @patch("shopping_list.config")
    @patch("shopping_list.open", side_effect=FileNotFoundError)
    def test_load_from_journal_file_not_found(self, mock_open, mock_config):
        # Mock config to provide journaldir
        mock_config.get_str.return_value = "/mock/journal/dir"
        mock_config.default_journal_dir = "/mock/default/dir"

        shopping_list = ShoppingList(self.mock_logger)
        shopping_list.load_from_journal()

        # Assertions
        self.mock_logger.info.assert_any_call("Loading shopping list from journal")
        self.mock_logger.error.assert_called_once_with("File not found: /mock/journal/dir/Colonisation.json")

    @patch("shopping_list.config")
    @patch("shopping_list.open", new_callable=mock_open, read_data='Invalid JSON')
    def test_load_from_journal_json_decode_error(self, mock_open, mock_config):
        # Mock config to provide journaldir
        mock_config.get_str.return_value = "/mock/journal/dir"
        mock_config.default_journal_dir = "/mock/default/dir"

        shopping_list = ShoppingList(self.mock_logger)
        shopping_list.load_from_journal()

        # Assertions
        self.mock_logger.info.assert_any_call("Loading shopping list from journal")
        self.mock_logger.error.assert_called_once_with("Error decoding JSON from file /mock/journal/dir/Colonisation.json: Expecting value: line 1 column 1 (char 0)")

if __name__ == "__main__":
    unittest.main()
