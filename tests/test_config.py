import os
from configparser import ConfigParser
from pathlib import Path

import pytest

from pystatis import config


@pytest.fixture()
def config_() -> ConfigParser:
    old_config = config.load_config()
    config.delete_config()
    yield config.config
    config.config = old_config
    config.write_config()


def test_config_path():
    assert (
        config._build_config_file_path()
        == Path(config.DEFAULT_CONFIG_DIR) / "config.ini"
    )
    assert config.get_cache_dir() == str(Path(config.DEFAULT_CONFIG_DIR) / "data")


def test_init_config_is_run_on_import(config_):
    assert isinstance(config_, ConfigParser)
    assert config._build_config_file_path().exists()
    assert Path(config.get_cache_dir()).exists()


def test_load_config(config_):
    assert config_.has_section("settings")
    assert config_.has_option("settings", "supported_db")
    assert config_.has_section("data")
    assert config_.has_option("data", "cache_dir")

    for section in config.get_supported_db():
        assert config_.has_section(section)

        assert config_.options(section) == [
            "base_url",
            "username",
            "password",
            "doku",
        ]

        assert config_.get(section, "username") == ""
        assert config_.get(section, "password") == ""


def test_missing_file(config_, caplog):
    (Path(config.DEFAULT_CONFIG_DIR) / "config.ini").unlink()

    assert not config.config_exists()

    caplog.clear()

    config_ = config.load_config()
    assert not config_.sections()

    for record in caplog.records:
        assert record.levelname == "CRITICAL"


def test_setup_credentials(config_):
    for db in config.get_supported_db():
        for field in ["username", "password"]:
            if field == "username":
                os.environ[f"PYSTATIS_{db.upper()}_API_{field.upper()}"] = "test"
            else:
                os.environ[f"PYSTATIS_{db.upper()}_API_{field.upper()}"] = "test123!"

    config.setup_credentials()

    for db in config.get_supported_db():
        assert config_[db]["username"] == "test"
        assert config_[db]["password"] == "test123!"


def test_supported_db():
    db = config.get_supported_db()
    assert isinstance(db, list)
    assert isinstance(db[0], str)
