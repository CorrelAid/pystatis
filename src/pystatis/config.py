"""Module for handling `config.ini` files.

This package stores core information in the `config.ini`, which is stored under the user home directory, unless the user specifies otherwise.
The parent directory for the `config.ini` is called after the package name by default.
The `config.ini` holds all relevant information about all supported databases like user credentials.
If there is no `config.ini` in the given `config_dir`, a default config will be created with empty credentials. Subsequent calls to other `pystatis` functions will throw an error until the user has filled in the credentials.
`init_config` is executed automatically when the package is imported for the first time. It can be called manually to change the default config directory.
"""
import logging
import os
from configparser import ConfigParser
from pathlib import Path

PKG_NAME = __name__.split(".", maxsplit=1)[0]

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = str(Path().home() / f".{PKG_NAME}")
CUSTOM_CONFIG_PATH = ""
SUPPORTED_DB = ["GENESIS", "ZENSUS"]


def init_config(config_dir: str = DEFAULT_CONFIG_DIR) -> None:
    """Create a new config .ini file in the given directory.

    One-time function to be called for new users to create a new `config.ini` with default values (empty credentials).

    Args:
        config_dir (str, optional): Path to the root config directory. Defaults to the user home directory.
    """
    global CUSTOM_CONFIG_PATH

    CUSTOM_CONFIG_PATH = (
        config_dir if config_dir != DEFAULT_CONFIG_DIR else DEFAULT_CONFIG_DIR
    )

    if not build_config_file().exists():
        config = create_default_config()
        write_config(config)

        logger.info("New config was created. Path: %s.", config_dir)


def setup_credentials() -> None:
    """Setup credentials for all supported databases."""
    config = load_config()

    for db in get_supported_db():
        config[db]["username"] = get_user_input("username", db)
        config[db]["password"] = get_user_input("password", db)

    write_config(config)

    logger.info(
        "Config was updated with latest credentials. Path: %s.",
        build_config_file(),
    )


def build_config_file() -> Path:
    return Path(CUSTOM_CONFIG_PATH) / "config.ini"


def get_user_input(db: str, field: str) -> str:
    env_var = os.environ.get(f"PYSTATIS_{db.upper()}_API_{field.upper()}")

    if env_var is not None:
        return env_var

    user_input = input(f"Please enter your {field} for the database {db}:")
    print("You entered: " + user_input)

    return user_input


def load_config(config_file: Path | None = None) -> ConfigParser:
    if config_file is None:
        config_file = build_config_file()

    config = ConfigParser()
    successful_reads = config.read(config_file)

    if not successful_reads:
        logger.critical(
            "Error while loading the config file. Could not find %s. "
            "Please make sure to run init_config() first. ",
            config_file,
        )

    return config


def write_config(config: ConfigParser, config_file: Path | None = None) -> None:
    if config_file is None:
        config_file = build_config_file()

    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)

    with open(config_file, "w", encoding="utf-8") as fp:
        config.write(fp)


def create_default_config() -> ConfigParser:
    config = ConfigParser()

    config["SETTINGS"] = {
        "active_db": "",
        "supported_db": ",".join(SUPPORTED_DB),
    }

    config["GENESIS"] = {
        "base_url": "https://www-genesis.destatis.de/genesisWS/rest/2020/",
        "username": "",
        "password": "",
        "doku": "https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf",
    }

    config["ZENSUS"] = {
        "base_url": "https://ergebnisse2011.zensus2022.de/api/rest/2020/",
        "username": "",
        "password": "",
        "doku": "https://ergebnisse2011.zensus2022.de/datenbank/misc/ZENSUS-Webservices_Einfuehrung.pdf",
    }

    config["DATA"] = {"cache_dir": str(Path(CUSTOM_CONFIG_PATH) / "data")}

    cache_dir = Path(config["DATA"]["cache_dir"])
    if not cache_dir.exists():
        cache_dir.mkdir()

    return config


def get_supported_db() -> list[str]:
    return SUPPORTED_DB


init_config()
