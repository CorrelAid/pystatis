import re
from configparser import ConfigParser
from pathlib import Path

import pytest

from pystatis.profile import change_password, remove_result
from tests.test_http_helper import _generic_request_status


@pytest.fixture()
def cache_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return Path(temp_dir)


def test_change_password(mocker, cache_dir):
    # mock configparser to be able to test writing of new password
    config = ConfigParser()
    config["GENESIS API"] = {
        "base_url": "mocked_url",
        "username": "JaneDoe",
        "password": "password",
    }
    mocker.patch("pystatis.profile.load_config", return_value=config)
    mocker.patch(
        "pystatis.profile.load_data",
        return_value=str(_generic_request_status().text),
    )
    mocker.patch(
        "pystatis.profile.get_config_path_from_settings",
        return_value=cache_dir / "config.ini",
    )

    response = change_password("new_password")

    assert response == str(_generic_request_status().text)


def test_change_password_keyerror(mocker, cache_dir):
    # define empty config (no password)
    mocker.patch(
        "pystatis.profile.load_config", return_value={"GENESIS API": {}}
    )
    mocker.patch(
        "pystatis.profile.load_data",
        return_value=str(_generic_request_status().text),
    )
    mocker.patch(
        "pystatis.profile.get_config_path_from_settings",
        return_value=cache_dir / "config.ini",
    )

    with pytest.raises(KeyError) as e:
        change_password("new_password")
    assert (
        "Password not found in config! Please make sure \
            init_config() was run properly & your user data is set correctly!"
        in str(e.value)
    )


def test_remove_result(mocker):
    mocker.patch(
        "pystatis.profile.load_data",
        return_value=str(_generic_request_status().text),
    )

    response = remove_result("11111-0001")

    assert response == str(_generic_request_status().text)
