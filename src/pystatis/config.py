"""Module for handling settings.ini and config.ini files.

This package stores core information in the settings.ini, which is stored under the user home directory.
The parent directory for the settings.ini is called after the package name.
The settings.ini gets automatically created by importing this package, if it does not exist already.
The config.ini is stored in a directory that is configured in the settings.ini via `config_dir`.
The config.ini holds all revelant information about the usage of GENESIS API like credentials.
If there is no config.ini in the given config_dir, a default config will be created with empty credentials.
"""
import logging
from configparser import ConfigParser
from pathlib import Path

PKG_NAME = __name__.split(".", maxsplit=1)[0]

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = Path().home() / f".{PKG_NAME}"
DEFAULT_SETTINGS_FILE = DEFAULT_CONFIG_DIR / "settings.ini"


def create_settings() -> None:
    """Create a settings.ini file within the default config folder in the user home directory."""
    if not DEFAULT_SETTINGS_FILE.exists():
        default_settings = ConfigParser()
        default_settings["SETTINGS"] = {"config_dir": str(DEFAULT_CONFIG_DIR)}

        _write_config(default_settings, DEFAULT_SETTINGS_FILE)
        logger.info(
            "Settings file was created. Path: %s.", DEFAULT_SETTINGS_FILE
        )


def load_settings() -> ConfigParser:
    """Load the config from settings.ini.

    Returns:
        ConfigParser: Sections and key-value pairs from settings.ini.
    """
    settings_file = DEFAULT_SETTINGS_FILE

    settings = ConfigParser()
    settings.read(settings_file)

    return settings


def get_config_path_from_settings() -> Path:
    """Return full local path to config.ini.

    Returns:
        Path: Path to config_dir / config.ini.
    """
    settings = load_settings()
    return Path(settings.get("SETTINGS", "config_dir")) / "config.ini"


def init_config(
    username: str, password: str, config_dir: Path = DEFAULT_CONFIG_DIR
) -> None:
    """One-time function to be called for new users to create a new config.ini with default values.

    Stores username and password for the GENESIS API, among other settings.

    Args:
        username (str): username used to login to GENESIS-Online.
        password (str): password used to login to GENESIS-Online.
        config_dir (Path, optional): Path to the root config directory. Defaults to the user home directory.
    """
    default_settings = load_settings()
    default_settings["SETTINGS"]["config_dir"] = str(config_dir)

    _write_config(default_settings, DEFAULT_SETTINGS_FILE)
    logger.info(
        "Settings file updated: config_dir set to %s. Path: %s.",
        config_dir,
        DEFAULT_SETTINGS_FILE,
    )

    config_file = get_config_path_from_settings()
    config = _create_default_config()
    config["GENESIS API"]["username"] = username
    config["GENESIS API"]["password"] = password
    _write_config(config, config_file)

    cache_dir = Path(config["DATA"]["cache_dir"])
    if not cache_dir.exists():
        cache_dir.mkdir()

    logger.info("New config was created. Path: %s.", config_file)


def load_config() -> ConfigParser:
    """Load the config from config.ini.

    Returns:
        ConfigParser: Sections and key-value pairs from config.ini.
    """
    config_file = get_config_path_from_settings()
    config = _load_config(config_file)

    if config.has_section("GENESIS API"):
        if not config.get("GENESIS API", "username") or not config.get(
            "GENESIS API", "password"
        ):
            logger.critical(
                "Username and/or password are missing! "
                "Please make sure to fill in your username and password for GENESIS API. "
                "Path: %s.",
                config_file,
            )

    return config


def _write_config(config: ConfigParser, config_file: Path) -> None:
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)

    with open(config_file, "w", encoding="utf-8") as fp:
        config.write(fp)


def _load_config(config_file: Path) -> ConfigParser:
    config = ConfigParser()
    successful_reads = config.read(config_file)

    if not successful_reads:
        logger.critical(
            "Error while loading the config file. Could not find %s. "
            "Please make sure to run init_config() first. ",
            config_file,
        )

    return config


def _create_default_config() -> ConfigParser:
    config = ConfigParser()
    settings = load_settings()
    config["GENESIS API"] = {
        "base_url": "https://www-genesis.destatis.de/genesisWS/rest/2020/",
        "username": "",
        "password": "",
        "doku": "https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf",
    }

    config["DATA"] = {
        "cache_dir": str(Path(settings["SETTINGS"]["config_dir"]) / "data")
    }

    return config


create_settings()
