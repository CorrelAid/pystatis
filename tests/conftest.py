import sys

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "filter_query_parameters": ["username", "password"],
    }


@pytest.fixture
def vcr_cassette_name(request):
    """Name of the VCR cassette"""
    f = request.function
    name = request.node.name
    mark = f.pytestmark[0]
    args = mark.args
    params = args[1]

    if "table_name" in args[0]:
        param = [param for param in params if param[0] in name][0]
        table_name = param[0]
        return table_name

    return name
