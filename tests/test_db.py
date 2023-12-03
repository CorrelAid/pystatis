import logging
from configparser import RawConfigParser

import pytest

from pystatis import config, db
from pystatis.exception import PystatisConfigError


@pytest.fixture()
def config_() -> RawConfigParser:
    old_config = config.load_config()
    config.delete_config()
    yield config.config
    config.config = old_config
    config.write_config()


@pytest.mark.parametrize("name", ["genesis", "zensus", "regio"])
def test_set_db(config_, name: str):
    db.set_db(name)

    assert db.get_db() == name


def test_set_db_with_invalid_name():
    with pytest.raises(ValueError):
        db.set_db("invalid_db_name")


def test_set_db_without_credentials(config_, caplog):
    caplog.clear()
    caplog.set_level(logging.CRITICAL)

    db.set_db("genesis")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "CRITICAL"
    assert (
        caplog.records[0].message
        == "No credentials for genesis found. Please run `setup_credentials()`."
    )


def test_get_db_without_set_db(config_):
    with pytest.raises(PystatisConfigError):
        db.get_db()


def test_get_db_settings(config_):
    db.set_db("genesis")
    settings = db.get_db_settings()
    assert isinstance(settings, tuple)
    assert len(settings) == 3
    assert all(isinstance(setting, str) for setting in settings)
