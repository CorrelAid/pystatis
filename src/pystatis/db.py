"""Module provides functions to set the active database and get active database properties."""
import logging

from pystatis import config
from pystatis.cache import normalize_name

logger = logging.getLogger(__name__)


def identify_db(name: str) -> list[str]:
    """Identify the required database by matching the item code to the database regex.

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


def check_db_credentials(db_name: str) -> bool:
    """
    Checks if a username and password is stored for the specified database.

    Args:
        db_name: Name of database to check credentials for.

    Returns:
        TRUE if credentials were found, FALSE otherwise.
    """
    return get_db_user(db_name) != "" and get_db_pw(db_name) != ""
