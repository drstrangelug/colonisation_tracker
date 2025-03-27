"""
Example EDMC plugin.

It adds a single button to the EDMC interface that displays the number of times it has been clicked.
"""
from __future__ import annotations

import logging
import tkinter as tk
from tkinter import *
from itertools import islice
from tkinter import ttk

from config import appname, config
from market_handler import commodity_names
from building_tracker import BuildingTracker

# This **MUST** match the name of the folder the plugin is in.
PLUGIN_NAME = "ColonisationTracker"

logger = logging.getLogger(f"{appname}.{PLUGIN_NAME}")
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

TARGET_SYSTEM='Col 285 Sector VS-Z b14-7'
TARGET_VESSEL='System Colonisation Ship'

class ColonisationTracker:
    """
    ClickCounter implements the EDMC plugin interface.

    It adds a button to the EDMC UI that displays the number of times it has been clicked, and a preference to set
    the number directly.
    """

    
bt = BuildingTracker(logger,PLUGIN_NAME)
ct = ColonisationTracker()

def journal_entry(
        cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[str]:
        if entry['event'] in ('Cargo', 'MarketBuy', 'MarketSell','Location','FDSJump','Docked','Undocked','StartUp'):
            bt.process_event(entry['event'], entry, state)
        else:
            logger.info(f"Ignoring event {entry['event']}")

# Note that all of these could be simply replaced with something like:
# plugin_start3 = cc.on_load
def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.

    See PLUGINS.md#startup
    """
    return bt.on_load()


def plugin_stop() -> None:
    """
    Handle shutdown of the plugin.

    See PLUGINS.md#shutdown
    """
    return bt.on_unload()


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame | None:
    """
    Handle preferences tab for the plugin.

    See PLUGINS.md#configuration
    """
    return bt.setup_preferences(parent, cmdr, is_beta)


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Handle any changed preferences for the plugin.

    See PLUGINS.md#configuration
    """
    return bt.on_preferences_closed(cmdr, is_beta)


def plugin_app(parent: tk.Frame) -> tk.Frame | None:
    """
    Set up the UI of the plugin.

    See PLUGINS.md#display
    """
    return bt.setup_main_ui(parent)


# Example usage:
# data = read_file_to_object("path/to/your/file.json")
# logger.info(f"Loaded data: {data}")