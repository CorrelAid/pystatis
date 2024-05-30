"""Module provides wrapper for Profile GENESIS REST-API functions."""

import logging
from typing import cast

from pystatis import db
from pystatis.http_helper import load_data

logger = logging.getLogger(__name__)


def change_password(db_name: str, new_password: str) -> str:
    """
    Changes Genesis REST-API password and updates local config.

    Args:
        new_password (str): New password for the Genesis REST-API
        db_name (str): Database for which the password should be changed (genesis, zensus, regio)

    Returns:
        str: text response from Destatis
    """
    params = {
        "new": new_password,
        "repeat": new_password,
    }

    # change remote password
    response_text = load_data(endpoint="profile", method="password", params=params, db_name=db_name)
    # change local password
    db.set_pw(db_name, new_password)

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
    response_text = load_data(endpoint="profile", method="removeresult", params=params)

    return cast(str, response_text)
