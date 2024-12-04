"""Module provides functions to set the active database and get active database properties."""

import logging

from pystatis import config
from pystatis.cache import normalize_name
from pystatis.exception import PystatisConfigError

logger = logging.getLogger(__name__)


def identify_db_matches(table_name: str) -> list[str]:
    """Identify possible databases by matching the item code to the database regex.

    Args:
        name (str): Query parameter 'name' corresponding to the item code.

    Returns:
        db_match (list[str]): List of matching databases.

    Raises:
        ValueError: If no db match was found.
    """
    regex_db = config.get_db_identifiers()

    # Strip optional leading * and trailing job id
    table_name = normalize_name(table_name).lstrip("*")

    # Get list of matching dbs
    db_matches = [db_name for db_name, reg in regex_db.items() if reg.match(table_name)]

    if db_matches:
        return db_matches
    else:
        raise ValueError(
            f"Could not determine the database for the table '{table_name}'."
        )


def select_db_by_credentials(db_matches: list[str]) -> str:
    """Out of a selection of db candidates, select the first that has existing
    credentials.

    Args:
        db_matches (list[str]): Possible DBs to choose from.

    Returns:
        db_name (str): Identified database.

    Raises:
        PystatisConfigError: If no credentials exist for any db candidate.
    """
    for db_name in db_matches:
        # Return first hit with existing credentials.
        if check_credentials(db_name):
            return db_name

    raise PystatisConfigError(
        "Missing credentials!\n"
        f"To access this item you need to be a registered user of: {db_matches} \n"
        "Please run setup_credentials()."
    )


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
