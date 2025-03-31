import unittest
import sys
from unittest.mock import MagicMock, patch, mock_open
configMock = MagicMock()
sys.modules['config'] = configMock
from shopping_list import ShoppingList



class TestShoppingList(unittest.TestCase):
    def setUp(self):
        # Mock logger
        self.mock_logger = MagicMock()
        configMock.get_str=MagicMock(return_value='./testdata/')

    @patch("shopping_list.config")
    #@patch("shopping_list.open", new_callable=mock_open, read_data='{"StarSystem": "TestSystem", "DeliveryStation": "TestStation", "Materials": {"Item1": 10}}')
    def test_load_from_journal_success(self, mock_config):
        # Mock config to provide journaldir
        mock_config.get_str.return_value = "./testdata"
        mock_config.default_journal_dir = "./testdata"

        shopping_list = ShoppingList(self.mock_logger)
        shopping_list.load_from_journal()

        # Assertions
        self.mock_logger.info.assert_any_call("Loading shopping list from journal")
        self.assertEqual(shopping_list.target_system, "Pequenenses")
        self.assertEqual(shopping_list.target_station, "System Colonisation Ship")
        self.assertEqual(shopping_list.shopping_list['ceramiccomposites'], 529)

if __name__ == "__main__":
    unittest.main()
