"""Module provides wrapper for HelloWorld GENESIS REST-API functions."""

import requests

from pystatis import db
from pystatis.http_helper import _check_invalid_status_code


def whoami(db_name: str) -> str:
    """
    Wrapper method which constructs a URL for testing the Destatis API
    whoami method, which returns host name and IP address.

    Args:
        db_name (str): Name of the database to test

    Returns:
        str: text test response from Destatis
    """
    url = f"{db.get_db_host(db_name)}" + "helloworld/whoami"

    response = requests.get(url, timeout=(1, 15))

    _check_invalid_status_code(response)

    return str(response.text)


def logincheck(db_name: str) -> str:
    """
    Wrapper method which constructs a URL for testing the Destatis API
    logincheck method, which tests the login credentials (from the config.ini).

    Args:
        db_name (str): Name of the database to login to

    Returns:
        str: text logincheck response from Destatis
    """
    db_host, db_user, db_pw = db.get_db_settings(db_name)
    url = f"{db_host}helloworld/logincheck"

    params = {
        "username": db_user,
        "password": db_pw,
    }

    response = requests.get(url, params=params, timeout=(1, 15))

    # NOTE: Cannot use get_data_from_endpoint due to colliding
    # and misleading usage of "Status" key in API response
    _check_invalid_status_code(response)

    return str(response.text)
