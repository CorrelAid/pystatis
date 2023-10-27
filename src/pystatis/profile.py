"""Module provides wrapper for Profile GENESIS REST-API functions."""

import logging
from typing import cast

from pystatis.config import _write_config, load_config
from pystatis.http_helper import load_data

logger = logging.getLogger(__name__)


def change_password(new_password: str) -> str:
    """
    Changes Genesis REST-API password and updates local config.

    Args:
        new_password (str): New password for the Genesis REST-API

    Returns:
        str: text response from Destatis
    """
    params = {
        "new": new_password,
        "repeat": new_password,
    }

    # load config.ini beforehand, to ensure passwords are changed at the same time
    config = load_config()
    try:
        config["GENESIS API"]["password"]
    except KeyError as e:
        raise KeyError(
            "Password not found in config! Please make sure \
            init_config() was run properly & your user data is set correctly!",
        ) from e

    # change remote password
    response_text = load_data(
        endpoint="profile", method="password", params=params
    )
    # change local password
    config["GENESIS API"]["password"] = new_password
    _write_config(config, get_config_path_from_settings())

    logger.info("Password changed successfully!")

    return cast(str, response_text)


def remove_result(name: str, area: str = "all") -> str:
    """
    Remove 'Ergebnistabellen' from the the permission space 'area'.
    Should only apply for manually saved data, visible in 'Meine Tabellen' in the Web Interface.

    Args:
        name (str): 'Ergebnistabelle' to be removed
        area (str): permission area in which the 'Ergebnistabelle' resides

    Returns:
        str: text response from Destatis
    """
    params = {"name": name, "area": area, "language": "de"}

    # remove 'Ergebnistabelle' with previously defined parameters
    response_text = load_data(
        endpoint="profile", method="removeresult", params=params
    )

    return cast(str, response_text)
