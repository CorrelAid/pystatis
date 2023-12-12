import logging
from configparser import ConfigParser

import pytest

from pystatis import config, db
from pystatis.exception import PystatisConfigError


@pytest.fixture()
def config_() -> ConfigParser:
    old_config = config.load_config()
    config.delete_config()
    yield config.config
    config.config = old_config
    config.write_config()


def test_get_db_settings(config_):
    settings = db.get_db_settings("genesis")
    assert isinstance(settings, tuple)
    assert len(settings) == 3
    assert all(isinstance(setting, str) for setting in settings)


def test_set_db_pw(config_):
    db.set_db_pw("genesis", "test_pw")
    assert db.get_db_pw("genesis") == "test_pw"


@pytest.mark.parametrize(
    "name, expected_db",
    [
        ("12345-6789", "genesis"),
        ("1234A-6789", "zensus"),
        ("21111-01-03-4", "regio"),
        ("21111-01-03-4-B", "regio"),
    ],
)
def test_match_db(config_, name, expected_db):
    assert db.match_db(name) == expected_db


def test_match_db_with_multiple_matches(config_):
    config_.set("genesis", "username", "test")
    config_.set("genesis", "password", "test")
    assert db.match_db("1234567890") == "genesis"

    config_.set("genesis", "username", "")
    config_.set("genesis", "password", "")
    config_.set("regio", "username", "test")
    config_.set("regio", "password", "test")
    assert db.match_db("1234567890") == "regio"
