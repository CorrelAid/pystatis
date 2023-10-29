import re

import pytest

from pystatis.profile import change_password, remove_result
from pystatis.config import init_config, load_config
from pystatis import db
from tests.test_http_helper import _generic_request_status


@pytest.fixture()
def config_dir(tmp_path_factory) -> str:
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return temp_dir


def test_change_password(mocker, config_dir):
    # mock configparser to be able to test writing of new password
    init_config(config_dir)
    config = load_config()

    assert config["genesis"]["password"] == ""

    mocker.patch(
        "pystatis.profile.load_data",
        return_value=_generic_request_status(),
    )

    db.set_db("genesis")
    response = change_password("new_password")
    config = load_config()

    assert config["genesis"]["password"] == "new_password"


def test_remove_result(mocker):
    mocker.patch(
        "pystatis.profile.load_data",
        return_value=str(_generic_request_status().text),
    )

    response = remove_result("11111-0001")

    assert response == str(_generic_request_status().text)
