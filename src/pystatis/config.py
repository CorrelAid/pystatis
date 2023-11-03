"""Module for handling `config.ini` files.

This package stores core information in the `config.ini`, which is stored under the user home directory.
The user can change the default config directory by setting the environment variable `PYSTATIS_CONFIG_DIR` or pass a custom directory to the `init_config` function.
The current config directory is always stored in the `settings.ini` file, which is located under the default config directory, which the user can not change.
If the user does not specify a custom config directory, the default config directory is used, which is `~/.pystatis` on Linux and `%APPDATA%/.pystatis` on Windows.
The `config.ini` holds all relevant information about all supported databases like user credentials.
When the package is loaded for the first time, a default config will be created with empty credentials. Subsequent calls to other `pystatis` functions will throw an error until the user has filled in the credentials.
"""
import logging
import os
from configparser import RawConfigParser
from pathlib import Path

PKG_NAME = __name__.split(".", maxsplit=1)[0]
DEFAULT_CONFIG_DIR = str(Path().home() / f".{PKG_NAME}")
SUPPORTED_DB = ["genesis", "zensus", "regio"]

logger = logging.getLogger(__name__)
config = None


def init_config() -> None:
    """Create a new config .ini file in the given directory.

    One-time function to be called for new users to create a new `config.ini` with default values (empty credentials).

    Args:
        config_dir (str, optional): Path to the root config directory. Defaults to the user home directory.
    """
    global config

    if not config_exists():
        config = create_default_config()
        write_config(config)
    else:
        config = load_config()


def config_exists() -> bool:
    """Check if the config file exists."""
    config_file = _build_config_file_path()
    return config_file.exists()


def setup_credentials() -> None:
    """Setup credentials for all supported databases."""
    global config

    for db in get_supported_db():
        config[db]["username"] = _get_user_input(db, "username")
        config[db]["password"] = _get_user_input(db, "password")

    write_config(config)

    logger.info(
        "Config was updated with latest credentials. Path: %s.",
        _build_config_file_path(),
    )


def _build_config_file_path() -> Path:
    """Build the path to the config file."""
    return Path(DEFAULT_CONFIG_DIR) / "config.ini"


def _get_user_input(db: str, field: str) -> str:
    """Get user input for the given database and field."""
    env_var = os.environ.get(f"PYSTATIS_{db.upper()}_API_{field.upper()}")

    if env_var is not None:
        return env_var

    user_input = input(f"Please enter your {field} for the database {db}:")
    print("You entered: " + user_input)

    return user_input


def load_config(config_file: Path | None = None) -> RawConfigParser:
    """Load a config from a file."""
    if config_file is None:
        config_file = _build_config_file_path()

    config = RawConfigParser()
    successful_reads = config.read(config_file)

    if not successful_reads:
        logger.critical(
            "Error while loading the config file. Could not find %s. "
            "Please make sure to run init_config() first. ",
            config_file,
        )

    return config


def write_config(config: RawConfigParser, config_file: Path = None) -> None:
    """Write a config to a file."""
    if config_file is None:
        config_file = _build_config_file_path()

    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True)

    cache_dir = Path(get_cache_dir())
    if not cache_dir.exists():
        cache_dir.mkdir()

    with open(config_file, "w", encoding="utf-8") as fp:
        config.write(fp)


def create_default_config() -> RawConfigParser:
    """Create a default config parser with empty credentials."""
    config = RawConfigParser()

    config.add_section("settings")
    config.set("settings", "active_db", "")
    config.set("settings", "supported_db", ",".join(SUPPORTED_DB))

    config.add_section("genesis")
    config.set(
        "genesis",
        "base_url",
        "https://www-genesis.destatis.de/genesisWS/rest/2020/",
    )
    config.set("genesis", "username", "")
    config.set("genesis", "password", "")
    config.set(
        "genesis",
        "doku",
        "https://www-genesis.destatis.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf",
    )

    config.add_section("zensus")
    config.set(
        "zensus",
        "base_url",
        "https://ergebnisse2011.zensus2022.de/api/rest/2020/",
    )
    config.set("zensus", "username", "")
    config.set("zensus", "password", "")
    config.set(
        "zensus",
        "doku",
        "https://ergebnisse2011.zensus2022.de/datenbank/misc/ZENSUS-Webservices_Einfuehrung.pdf",
    )

    config.add_section("regio")
    config.set(
        "regio",
        "base_url",
        "https://www.regionalstatistik.de/genesisws/rest/2020/",
    )
    config.set("regio", "username", "")
    config.set("regio", "password", "")
    config.set(
        "regio",
        "doku",
        "https://www.regionalstatistik.de/genesis/misc/GENESIS-Webservices_Einfuehrung.pdf",
    )

    config.add_section("data")
    cache_dir = Path(DEFAULT_CONFIG_DIR) / "data"
    config.set("data", "cache_dir", cache_dir.as_posix())

    return config


def get_supported_db() -> list[str]:
    """Get a list of supported database names."""
    return SUPPORTED_DB


def get_cache_dir() -> str:
    """Get the cache directory."""
    return config.get("data", "cache_dir")


def delete_config() -> None:
    """Delete the config file."""
    if config_exists():
        config_file = _build_config_file_path()
        config_file.unlink()
        init_config()

    logger.info("Config was deleted. Path: %s.", config_file)


init_config()
