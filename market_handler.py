from config import appname, config

import pathlib
import logging
import json  # Add this import for JSON handling

def commodity_names(logger: logging.Logger) -> dict:
    journaldir = config.get_str('journaldir')
    if journaldir is None or journaldir == '':
        journaldir = config.default_journal_dir
    path = pathlib.Path(f"{journaldir}/Market.json")

    try:
        with(open(path, 'r')) as f:
            data = json.load(f)
            ret = {}
            for item in data['Items']:
                ret[item['Name'].lstrip("$").removesuffix("_name;")] = item['Name_Localised']
            return ret
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {filepath}: {e}")
        return {}

