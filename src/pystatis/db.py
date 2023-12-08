"""Module provides functions to set the active database and get active database properties."""
import logging
import re

from pystatis import config
from pystatis.cache import normalize_name
from pystatis.exception import PystatisConfigError

logger = logging.getLogger(__name__)


def match_db(name: str) -> str:
    """Match item code to database.

    Args:
        name (str): Query parameter 'name' corresponding to item code.

    Returns:
        (str): Name of matching database.
    """
    supported_dbs = config.get_supported_db()
    regex_db = config.get_regex()

    # Strip optional leading * and trailing job id
    name = normalize_name(name).lstrip("*")

    # Get list of matching dbs
    db_match = [
        idb for idb, irx in zip(supported_dbs, regex_db) if re.match(irx, name)
    ]

    if db_match:
        # If more than one db matches it must be a Cube (provided all regexing works as intended).
        # --> Choose db based on available credentials.
        if len(db_match) > 1:
            for check_db in db_match:
                if get_db_user(check_db) and get_db_pw(check_db):
                    return check_db

            raise PystatisConfigError(
                "You lack the necessary credentials to access this item. "
                "Please run setup_credentials()."
            )
        else:
            return db_match[0]
    else:
        return ""


def get_db_host(db_name: str) -> str:
    return config.config[db_name]["base_url"]


def get_db_user(db_name: str) -> str:
    return config.config[db_name]["username"]


def get_db_pw(db_name: str) -> str:
    return config.config[db_name]["password"]


def set_db_pw(db_name: str, new_pw: str) -> None:
    config.config.set(db_name, "password", new_pw)
    config.write_config()


def get_db_settings(db_name: str) -> tuple[str, str, str]:
    """Get database settings (host, user, password)."""
    return get_db_host(db_name), get_db_user(db_name), get_db_pw(db_name)
