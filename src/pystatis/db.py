"""Module provides functions to set the active database and get active database properties."""
import logging
import re

from pystatis import config
from pystatis.cache import normalize_name
from pystatis.exception import PystatisConfigError

logger = logging.getLogger(__name__)


def set_db(name: str) -> None:
    """Set the active database.

    Args:
        name (str): Name of the database. Must be one of the supported databases.
        See `pystatis.config.get_supported_db()`.
    """
    if name.lower() not in config.get_supported_db():
        raise ValueError(
            f"Database {name} not supported! Please choose one of {', '.join(config.get_supported_db())}"
        )
    config.config.set("settings", "active_db", name.lower())

    if not get_db_user() or not get_db_pw():
        logger.critical(
            "No credentials for %s found. Please run `setup_credentials()`.",
            name,
        )


def get_db() -> str:
    """Get the active database."""
    active_db = config.config.get("settings", "active_db")

    if not active_db:
        raise PystatisConfigError(
            "No active database set! Please run `set_db()`."
        )

    return active_db


def match_db(name: str) -> str:
    """Match item code to database.
    
    Args:
        name (str): Query parameter 'name' corresponding to item code.

    Returns: 
        db_name (str): Name of matching database. 
    """
    supported_dbs = config.get_supported_db()
    regex_db = config.get_regex()

    # Strip optional leading * and trailing job id
    name = normalize_name(name).lstrip("*")

    db_match = [idb for idb, irx in zip(supported_dbs, regex_db) if re.match(irx, name)]

    if db_match:
        # Return the first match for now (only cubes should have more than one match as they
        # can be found in GENESIS-online and RegioDB. Needs to be adjusted for advanced  
        # functionality, e.g. checking available credentials).
        db_name = db_match[0]
    else:
        db_name = ""

    return db_name


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
