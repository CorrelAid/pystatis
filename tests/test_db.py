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
    settings = db.get_settings("genesis")
    assert isinstance(settings, tuple)
    assert len(settings) == 3
    assert all(isinstance(setting, str) for setting in settings)


def test_set_db_pw(config_):
    db.set_pw("genesis", "test_pw")
    assert db.get_pw("genesis") == "test_pw"


@pytest.mark.parametrize(
    "name, expected_db",
    [
        ("12345-6789", "genesis"),
        ("1234A-6789", "zensus"),
        ("21111-01-03-4", "regio"),
        ("21111-01-03-4-B", "regio"),
    ],
)
def test_identify_db_matches(config_, name, expected_db):
    assert db.identify_db_matches(name)[0] == expected_db


def test_identify_db_matches_no_match(config_):
    with pytest.raises(ValueError):
        db.identify_db_matches("test")


def test_identify_db_with_multiple_matches(config_):
    config_.set("genesis", "username", "test")
    config_.set("genesis", "password", "test")
    db_match = db.identify_db_matches("1234567890")
    for db_name in db_match:
        if db.check_credentials(db_name):
            break
    assert db_name == "genesis"

    config_.set("genesis", "username", "")
    config_.set("genesis", "password", "")
    config_.set("regio", "username", "test")
    config_.set("regio", "password", "test")
    db_match = db.identify_db_matches("1234567890")
    for db_name in db_match:
        if db.check_credentials(db_name):
            break
    assert db_name == "regio"


def test_select_db_by_credentials(config_):
    with pytest.raises(PystatisConfigError):
        db.select_db_by_credentials([])
