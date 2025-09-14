from configparser import RawConfigParser
from typing import Generator

import pytest

from pystatis import config
from pystatis.profile import change_password, remove_result
from tests.test_http_helper import _generic_request_status


@pytest.fixture()
def config_() -> Generator[RawConfigParser, None, None]:
    old_config = config.load_config()
    config.delete_config()
    yield config.config
    config.config = old_config
    config.write_config()


def test_change_password(mocker, config_):
    # mock configparser to be able to test writing of new password
    assert config_.get("genesis", "password") == ""

    mocker.patch(
        "pystatis.profile.load_data",
        return_value=_generic_request_status(),
    )

    change_password("genesis", "new_password")

    assert config_.get("genesis", "password") == "new_password"


def test_remove_result(mocker):
    mocker.patch(
        "pystatis.profile.load_data",
        return_value=str(_generic_request_status().text),
    )

    response = remove_result("11111-0001")

    assert response == str(_generic_request_status().text)
