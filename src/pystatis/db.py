"""Module provides functions to set the active database and get active database properties."""

import logging

from pystatis import config, db
from pystatis.cache import normalize_name
from pystatis.exception import PystatisConfigError

logger = logging.getLogger(__name__)


def identify_db_matches(name: str) -> list[str]:
    """Identify possible databases by matching the item code to the database regex.

    Args:
        name (str): Query parameter 'name' corresponding to the item code.

    Returns:
        db_match (list[str]): List of matching databases.
    """
    regex_db = config.get_db_identifiers()

    # Strip optional leading * and trailing job id
    name = normalize_name(name).lstrip("*")

    # Get list of matching dbs
    db_match = [db_name for db_name, reg in regex_db.items() if reg.match(name)]

    return db_match


def identify_db(name: str) -> str:
    """Identify database by matching with the provided item code.
    This is done by matching the item code to the database regex. If multiple matches exist, use the first with existing credentials.
    In this case, it must be a Cube (provided all regexing works as intended).

    Args:
        name (str): Query parameter 'name' corresponding to the item code.

    Returns:
        db_name (str): Identified database.
    """
    db_match = db.identify_db_matches(name)

    if db_match:
        for name in db_match:
            if db.check_credentials(name):
                db_name = name
                break
        else:
            raise PystatisConfigError(
                "Missing credentials!\n"
                f"To access this item you need to be a registered user of: {db_match} \n"
                "Please run setup_credentials()."
            )

    return db_name


def get_host(db_name: str) -> str:
    return config.config[db_name]["base_url"]


def get_user(db_name: str) -> str:
    return config.config[db_name]["username"]


def get_pw(db_name: str) -> str:
    return config.config[db_name]["password"]


def set_pw(db_name: str, new_pw: str) -> None:
    config.config.set(db_name, "password", new_pw)
    config.write_config()


def get_settings(db_name: str) -> tuple[str, str, str]:
    """Get database settings (host, user, password)."""
    return get_host(db_name), get_user(db_name), get_pw(db_name)


def check_credentials(db_name: str) -> bool:
    """
    Checks if a username and password is stored for the specified database.

    Args:
        db_name: Name of database to check credentials for.

    Returns:
        TRUE if credentials were found, FALSE otherwise.
    """
    return get_user(db_name) != "" and get_pw(db_name) != ""
