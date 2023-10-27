import logging

from pystatis.config import get_supported_db, load_config

config = load_config()  # this module works with a local copy of the config!
logger = logging.getLogger(__name__)


def set_db(name: str) -> None:
    """Set the active database."""
    if name.lower() not in get_supported_db():
        raise ValueError(
            f"Database {name} not supported! Please choose one of {get_supported_db()}"
        )
    config["SETTINGS"]["active_db"] = name.lower()


def get_db() -> str:
    """Get the active database."""
    if config["SETTINGS"]["active_db"] == "":
        logger.critical("No active database set! Please run `set_db()`.")
    return config["SETTINGS"]["active_db"]


def get_db_host() -> str:
    return config[get_db()]["base_url"]


def get_db_user() -> str:
    return config[get_db()]["username"]


def get_db_pw() -> str:
    return config[get_db()]["password"]


def get_db_settings() -> tuple[str, str, str]:
    """Get the active database settings (host, user, password)."""
    return get_db_host(), get_db_user(), get_db_pw()
