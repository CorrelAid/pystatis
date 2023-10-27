"""Module provides wrapper for HelloWorld GENESIS REST-API functions."""

import requests

from pystatis import db
from pystatis.http_helper import _check_invalid_status_code


def whoami() -> str:
    """
    Wrapper method which constructs an URL for testing the Destatis API
    whoami method, which returns host name and IP address.

    Returns:
        str: text test response from Destatis
    """
    url = f"{db.get_db_host()}" + "helloworld/whoami"

    response = requests.get(url, timeout=(1, 15))

    _check_invalid_status_code(response)

    return str(response.text)


def logincheck() -> str:
    """
    Wrapper method which constructs an URL for testing the Destatis API
    logincheck method, which tests the login credentials (from the config.ini).

    Returns:
        str: text logincheck response from Destatis
    """
    url = f"{db.get_db_host()}" + "helloworld/logincheck"

    params = {
        "username": db.get_db_user(),
        "password": db.get_db_pw(),
    }

    response = requests.get(url, params=params, timeout=(1, 15))

    # NOTE: Cannot use get_data_from_endpoint due to colliding
    # and misleading usage of "Status" key in API response
    _check_invalid_status_code(response)

    return str(response.text)
