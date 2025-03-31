import logging
import json
import pathlib
from config import appname, config

class ShoppingList:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.load_from_journal()        

    def log(self, message: str) -> None:
        """
        Log a message to the logger.
        """
        self.logger.info(message)
        
    def load_from_journal(self) -> None:
        """
        Load the shopping list from the journal file.
        """
        self.log("Loading shopping list from journal")
        journaldir = config.get_str('journaldir')
        if journaldir is None or journaldir == '':
            journaldir = config.default_journal_dir
        filepath = pathlib.Path(f"{journaldir}/colonisation_tracker.json")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.target_system=data['StarSystem']
                self.target_station=data['DeliveryStation']
                self.shopping_list = data['Materials']
                self.log(f"Loaded shopping list from {filepath}")
        except FileNotFoundError:
            self.logger.error(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from file {filepath}: {e}")