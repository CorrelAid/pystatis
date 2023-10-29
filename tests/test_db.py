import logging
import re
from pathlib import Path

import pytest

from pystatis import config
from pystatis.db import get_db, set_db
from pystatis.exception import PystatisConfigError


@pytest.fixture()
def config_dir(tmp_path_factory) -> Path:
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    config.init_config(temp_dir)

    return temp_dir


@pytest.mark.parametrize("db", ["genesis", "zensus"])
def test_set_db(config_dir, db: str):
    set_db(db)

    assert get_db() == db


def test_set_db_with_invalid_name(config_dir):
    with pytest.raises(ValueError):
        set_db("invalid_db_name")


def test_set_db_without_credentials(config_dir, caplog):
    caplog.clear()
    caplog.set_level(logging.CRITICAL)

    set_db("genesis")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "CRITICAL"
    assert (
        caplog.records[0].message
        == "No credentials for genesis found. Please run `setup_credentials()`."
    )


def test_get_db_without_set_db(config_dir):
    with pytest.raises(PystatisConfigError):
        get_db()
