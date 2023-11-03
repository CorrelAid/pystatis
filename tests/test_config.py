import logging
import re
from configparser import ConfigParser
from pathlib import Path

import pytest

import pystatis.config
from pystatis.config import (
    DEFAULT_SETTINGS_FILE,
    _write_config,
    create_settings,
    get_config_path_from_settings,
    init_config,
    load_config,
    load_settings,
)


@pytest.fixture()
def config_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return Path(temp_dir)


@pytest.fixture(autouse=True)
def restore_settings():  # TODO: Unused?
    old_settings = load_settings()
    yield
    _write_config(old_settings, DEFAULT_SETTINGS_FILE)


def test_create_settings_is_run_on_import():
    assert DEFAULT_SETTINGS_FILE.exists() and DEFAULT_SETTINGS_FILE.is_file()


def test_create_settings(config_dir, mocker):
    mocker.patch.object(pystatis.config, "DEFAULT_CONFIG_DIR", config_dir)
    mocker.patch.object(
        pystatis.config, "DEFAULT_SETTINGS_FILE", config_dir / "settings.ini"
    )
    create_settings()

    assert (config_dir / "settings.ini").is_file()


def test_load_settings():
    settings = load_settings()

    assert isinstance(settings, ConfigParser)
    assert settings.has_option("SETTINGS", "config_dir")


def test_get_config_path_from_settings():
    config_path = get_config_path_from_settings()

    assert isinstance(config_path, Path)


def test_init_config_with_config_dir(config_dir, caplog):
    caplog.clear()
    caplog.set_level(logging.INFO)

    init_config("myuser", "mypw", config_dir)

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[1].levelname == "INFO"
    assert "Settings file updated" in caplog.text
    assert "New config was created" in caplog.text
    assert (config_dir / "data").exists()

    config = load_config()

    assert isinstance(config, ConfigParser)
    assert len(config.sections()) > 0
    assert config["DATA"]["cache_dir"] == str(config_dir / "data")
    assert len(list((config_dir / "data").glob("*"))) == 0

    config_file = get_config_path_from_settings()

    assert config_file.exists() and config_file.is_file()


def test_load_config(config_dir):
    init_config("myuser", "mypw123!", config_dir)
    config: ConfigParser = load_config()

    for section in ["GENESIS API", "DATA"]:
        assert config.has_section(section)

    assert config.options("GENESIS API") == [
        "base_url",
        "username",
        "password",
        "doku",
    ]
    assert config.options("DATA") == ["cache_dir"]

    assert config["GENESIS API"]["username"] == "myuser"
    assert config["GENESIS API"]["password"] == "mypw123!"


def test_missing_username(config_dir, caplog):
    init_config("", "", config_dir)

    caplog.clear()

    _ = load_config()

    assert caplog.records[0].levelname == "CRITICAL"
    assert "Username and/or password are missing!" in caplog.text


def test_missing_file(config_dir, caplog):
    init_config("", "", config_dir)
    (config_dir / "config.ini").unlink()

    caplog.clear()

    config = load_config()
    assert not config.sections()

    for record in caplog.records:
        assert record.levelname == "CRITICAL"
