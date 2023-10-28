import logging

from pystatis.config import config, get_supported_db, write_config

logger = logging.getLogger(__name__)


def set_db(name: str) -> None:
    """Set the active database."""
    if name.lower() not in get_supported_db():
        raise ValueError(
            f"Database {name} not supported! Please choose one of {', '.join(get_supported_db())}"
        )
    config["SETTINGS"]["active_db"] = name.lower()


def get_db() -> str:
    """Get the active database."""
    active_db = config["SETTINGS"]["active_db"]
    if not active_db:
        logger.critical("No active database set! Please run `set_db()`.")

    if not config[active_db]["username"] or not config[active_db]["password"]:
        logger.critical(
            "No credentials for %s found. Please run `setup_credentials()`.",
            active_db,
        )

    return active_db


def get_db_host() -> str:
    return config[get_db()]["base_url"]


def get_db_user() -> str:
    return config[get_db()]["username"]


def get_db_pw() -> str:
    return config[get_db()]["password"]


def set_db_pw(new_pw: str) -> None:
    config[get_db()]["password"] = new_pw
    write_config(config)


def get_db_settings() -> tuple[str, str, str]:
    """Get the active database settings (host, user, password)."""
    return get_db_host(), get_db_user(), get_db_pw()
