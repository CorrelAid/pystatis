"""Module provides functions to set the active database and get active database properties."""
import logging

from pystatis import config
from pystatis.exception import PystatisConfigError

logger = logging.getLogger(__name__)


def set_db(name: str) -> None:
    """Set the active database.

    Args:
        name (str): Name of the database. Must be one of the supported databases. See `pystatis.config.get_supported_db()`.
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


def get_db_host() -> str:
    return config.config[get_db()]["base_url"]


def get_db_user() -> str:
    return config.config[get_db()]["username"]


def get_db_pw() -> str:
    return config.config[get_db()]["password"]


def set_db_pw(new_pw: str) -> None:
    config.config.set(get_db(), "password", new_pw)
    config.write_config()


def get_db_settings() -> tuple[str, str, str]:
    """Get the active database settings (host, user, password)."""
    return get_db_host(), get_db_user(), get_db_pw()
