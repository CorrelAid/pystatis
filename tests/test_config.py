import logging
import os
import re
from configparser import ConfigParser
from pathlib import Path

import pytest

from pystatis.config import (
    _build_config_file_path,
    config,
    delete_config,
    get_cache_dir,
    get_supported_db,
    init_config,
    load_config,
    setup_credentials,
)


@pytest.fixture()
def config_dir(tmp_path_factory) -> str:
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return temp_dir


def test_init_config_is_run_on_import():
    assert isinstance(config, ConfigParser)
    assert _build_config_file_path().exists()


def test_custom_config_dir(config_dir, caplog):
    caplog.clear()
    caplog.set_level(logging.INFO)

    init_config(config_dir)
    config = load_config()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert "New config was created" in caplog.text
    assert Path(get_cache_dir()).exists()
    assert _build_config_file_path().exists()

    assert isinstance(config, ConfigParser)
    assert len(config.sections()) > 0
    assert get_cache_dir() == str(Path(config_dir) / "data")
    assert len(list((Path(get_cache_dir())).glob("*"))) == 0


def test_load_config(config_dir):
    init_config(config_dir)
    config = load_config()

    assert config.has_section("SETTINGS")
    assert config.has_option("SETTINGS", "active_db")
    assert config.has_option("SETTINGS", "supported_db")
    assert config.has_section("DATA")
    assert config.has_option("DATA", "cache_dir")

    for section in get_supported_db():
        assert config.has_section(section)

        assert config.options(section) == [
            "base_url",
            "username",
            "password",
            "doku",
        ]

        assert config[section]["username"] == ""
        assert config[section]["password"] == ""


def test_missing_file(config_dir, caplog):
    init_config(config_dir)
    (Path(config_dir) / "config.ini").unlink()

    caplog.clear()

    config = load_config()
    assert not config.sections()

    for record in caplog.records:
        assert record.levelname == "CRITICAL"


def test_delete_config(config_dir):
    init_config(config_dir)

    assert _build_config_file_path().exists()
    delete_config()
    assert not _build_config_file_path().exists()


def test_setup_credentials(config_dir):
    init_config(config_dir)

    for db in get_supported_db():
        for field in ["username", "password"]:
            if field == "username":
                os.environ[
                    f"PYSTATIS_{db.upper()}_API_{field.upper()}"
                ] = "test"
            else:
                os.environ[
                    f"PYSTATIS_{db.upper()}_API_{field.upper()}"
                ] = "test123!"

    setup_credentials()
    config = load_config()

    for db in get_supported_db():
        assert config[db]["username"] == "test"
        assert config[db]["password"] == "test123!"
