from __future__ import annotations
from config import config
import myNotebook as nb  # noqa: N813
import tkinter as tk
import logging
from tkinter import *
from itertools import islice
from tkinter import ttk
from market_handler import commodity_names
from cargo_manager import CargoManager
from shopping_list import ShoppingList


class BuildingTracker:
    def __init__(self, logger, PLUGIN_NAME) -> None:
        self.logger = logger
        self.PLUGIN_NAME=PLUGIN_NAME
        # Be sure to use names that wont collide in our config variables
        self.shopping_list = {
            "aluminium": 485,
            "ceramiccomposites": 529,
            "cmmcomposite": 487,
            "computercomponents": 64,
            "copper": 235,
            "foodcartridges": 91,
            "fruitandvegetables": 48,
            "insulatingmembrane": 335,
            "liquidoxygen": 1724,
            "medicaldiagnosticequipment": 13,
            "nonlethalweapons": 13,
            "polymers": 544,
            "powergenerators": 19,
            "semiconductors": 68,
            "steel": 0,
            "superconductors": 109,
            "titanium": 1760,
            "water": 748,
            "waterpurifiers": 38,
        }
        self.cargo_manager = CargoManager(logger)
        self.shopping_list = ShoppingList(logger)
        try:
            max = config.get_int('max_commodities')
            if max is None or not isinstance(max, int):
                max = 5
            self.max_commodities = tk.StringVar(value=str(max))
        except:
            self.max_commodities = tk.StringVar(value="5")
        self.logger.info(f"ColonyTracker instantiated, showing {self.max_commodities.get()} commodities")

    def on_load(self) -> str:
        self.commodity_names=commodity_names(self.logger)
        """
        on_load is called by plugin_start3 below.

        It is the first point EDMC interacts with our code after loading our module.

        :return: The name of the plugin, which will be used by EDMC for logging and for the settings window
        """
        return self.PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop below.

        It is the last thing called before EDMC shuts down. Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame | None:
        """
        setup_preferences is called by plugin_prefs below.

        It is where we can setup our own settings page in EDMC's settings window. Our tab is defined for us.

        :param parent: the tkinter parent that our returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        current_row = 0
        prefsFrame = nb.Frame(parent)

        # setup our config in a "Click Count: number"
        nb.Label(prefsFrame, text='Commodities count').grid(row=current_row)
        nb.EntryMenu(prefsFrame, textvariable=self.max_commodities).grid(row=current_row, column=1)
        current_row += 1  # Always increment our row counter, makes for far easier tkinter design.
        return prefsFrame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        # You need to cast to `int` here to store *as* an `int`, so that
        # `config.get_int()` will work for re-loading the value.
        self.logger.info(f"Setting max commodities to {int(self.max_commodities.get())}")
        config.set('max_commodities', int(self.max_commodities.get()))
        if ( int(self.max_commodities.get()) != self.last_count ):
            for child in self.frame.winfo_children():
                child.destroy()
            self.populate_shopping_list()

    def populate_shopping_list(self) -> None:
        current_row = 0
        sorted_list = {k: v for k, v in sorted(self.shopping_list.items(), key=lambda item: -item[1])}
        count = int(self.max_commodities.get())
        self.last_count = count
        self.labels={}
        for key, value in dict(islice(sorted_list.items(), count)).items():
            if value > 0:
                name=self.commodity_names[key]
                tk.Label(self.frame, text=f"{name}:",).grid(row=current_row, sticky=tk.W)
                valueLabel = tk.Label(self.frame, text=f"{value}")
                valueLabel.grid(row=current_row, column=1)
                self.labels[key] = valueLabel
            current_row += 1

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        self.style = ttk.Style()
        self.frame = frame
        self.populate_shopping_list()
        return frame

    def update_shopping_list(self, cargo_name:str, amount_sold:int)->None:
        if cargo_name in self.shopping_list:
            self.shopping_list[cargo_name] = self.shopping_list[cargo_name] - amount_sold
            if cargo_name in self.labels:
                self.labels[cargo_name].config(text=f"{self.shopping_list[cargo_name]}")
                self.logger.info(f"Updating shopping list for {cargo_name} to {self.shopping_list[cargo_name]}")

    def set_star_system(self, system: str) -> None:
        self.star_system=system
        self.logger.info(f"Set star system to {system}")
    
    def set_docked(self, system: str, station: str) -> None:
        self.docked=True
        self.star_system=system
        self.docked_at=station
        self.logger.info(f"Docked at {station} in {system}")
        
    def is_docker_at_colonisation_ship(self) -> bool:
        return self.docked and self.docked_at==TARGET_VESSEL and self.star_system==TARGET_SYSTEM

    def set_startup_location(self, entry: Dict[str, Any]) -> None:
        if hasattr(self, 'docked_at'):
            del self.docked_at
        if 'StarSystem' in entry:
            self.set_star_system(entry['StarSystem'])
        if 'Docked' in entry:
            self.docked = entry['Docked']
            self.logger.info(f"Starting docked status as {self.docked} from [{entry['Docked']}]")
            if 'StationName' in entry:
                self.docked_at = entry['StationName']
        if self.docked:
            self.logger.info(f"Starting in {self.star_system} docked at {self.docked_at}")
        else:
            self.logger.info(f"Starging in {self.star_system} in space")

    def cargo_update(
        self, cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]
    ) -> None:
        if 'Cargo' in state:
            sold_list = self.cargo_manager.update_cargo(state['Cargo'])
            
            if self.is_docker_at_colonisation_ship():
                self.update_shopping_list(cargoName, sold)

    def set_startup(self, entry: Dict[str, Any]) -> None:
        if 'StarSystem' in entry:
            self.set_star_system(entry['StarSystem'])
        if 'Docked' in entry:
            self.docked = entry['Docked']
            if 'StationName' in entry:
                stationName=entry['StationName']
                if '$EXT_PANEL_ColonisationShip' in stationName:
                    self.logger.info(f"Overriding station name")
                    self.docked_at = 'System Colonisation Ship'
                else:
                    self.logger.info(f"Using station name")
                    self.docked_at = stationName                
        if self.docked:
            self.logger.info(f"StartUp in {self.star_system} docked at {self.docked_at}")
        else:
            self.logger.info(f"StartUp in {self.star_system} in space")

    def process_event(self, event: str, entry: Dict[str, Any], state: Dict[str, Any]) -> None:
        if event in ('Cargo', 'MarketBuy', 'MarketSell') and 'Cargo' in state:
            self.cargo_update(entry)
        elif event == 'Location':
            self.set_startup_location(entry)
        elif event == 'FSDJump' and 'StarSystem' in entry:
            self.set_star_system(entry['StarSystem'])
        elif event == 'Docked' and all(k in entry for k in ('StarSystem', 'StationName_Localised')):
            self.set_docked(entry['StarSystem'], entry['StationName_Localised'])
        elif event == 'Undocked' and hasattr(self, 'docked_at'):
            self.logger.info(f"Undocked from {self.docked_at} in {self.star_system}")
            self.docked=False
            del self.docked_at
        elif event=='StartUp':
            self.logger.info(f'startup event {event}')
            self.set_startup(entry)
        else:
            self.logger.info(f"Ignoring event {event}")