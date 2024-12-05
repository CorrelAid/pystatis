from pystatis import logincheck, whoami
from tests.test_http_helper import _generic_request_status


def test_whoami(mocker):
    mocker.patch(
        "pystatis.helloworld.requests.get",
        return_value=_generic_request_status(),
    )
    mocker.patch("pystatis.db.get_host", return_value="genesis")

    response = whoami("genesis")

    assert response == str(_generic_request_status().text)


def test_logincheck(mocker):
    mocker.patch(
        "pystatis.helloworld.requests.get",
        return_value=_generic_request_status(),
    )
    mocker.patch(
        "pystatis.helloworld.requests.post",
        return_value=_generic_request_status(),
    )
    mocker.patch("pystatis.db.get_settings", return_value=("host", "user", "pw"))

    response = logincheck("genesis")

    assert response == str(_generic_request_status().text)
