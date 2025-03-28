import logging
import json
import pathlib
from config import appname, config

class CargoManager:
    def __init__(self, logger):
        self.logger = logger
        self.cargo={}
        self.scan_cargo_json()

    def log(self, message:str)->None:
        self.logger.info(message)

    def scan_cargo_json(self):
        """
        Scan the cargo.json file and update the cargo dictionary.
        """
        journaldir = config.get_str('journaldir')
        if journaldir is None or journaldir == '':
            journaldir = config.default_journal_dir
        filepath = pathlib.Path(f"{journaldir}/Cargo.json")
        try:
            self.log("Processing cargo.json")
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data['Inventory']:
                    self.log(f"Found cargo {item['Name']} (x {item['Count']})")
                    self.cargo[item['Name']] = item['Count']
            self.log(f"Loaded cargo data from {filepath}")
        except FileNotFoundError:
            self.logger.error(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from file {filepath}: {e}")

    def update_cargo(self, newManifest: dict[str, int]) -> dict[str, int]:
        sold_list={}
        for cargoName in self.cargo:
            if cargoName in self.cargo:
                if self.cargo.get(cargoName) > newManifest.get(cargoName):
                    sold = self.current_cargo.get(cargoName) - newManifest.get(cargoName)
                    if sold>0:
                        self.cargo[cargoName] = self.cargo[cargoName] - sold
                        self.logger.info(f"Sold {sold} of {cargoName}  - hold now has {self.cargo.get(cargoName,0)}")
                        sold_list[cargoName] = sold
                        if self.is_docker_at_colonisation_ship():
                            self.update_shopping_list(cargoName, sold)
                else:
                    bought = newManifest.get(cargoName) - self.cargo.get(cargoName)
                    if bought>0:
                        self.cargo[cargoName] = self.cargo[cargoName] + bought
                        self.logger.info(f"Bought {bought} of {cargoName} - hold now has {self.cargo.get(cargoName)}")
            else:
                bought = newManifest.get(cargoName)
                self.cargo[cargoName] = bought
                self.logger.info(f"Bought {bought} of {cargoName}")
        for cargoName in self.cargo:
            if cargoName not in newManifest:
                sold=self.cargo.get(cargoName)
                self.logger.info(f"Empty of {cargoName} [ {self.cargo.get(cargoName)} removed from hold]")
                sold_list[cargoName] = sold
