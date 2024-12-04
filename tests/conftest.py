import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization", "username", "password"],
        "filter_query_parameters": ["username", "password"],
        # see https://vcrpy.readthedocs.io/en/latest/configuration.html,
        # need to add body here as Genesis v5 uses POST requests
        # and params now go into the body and not the query
        "match_on": [
            "method",
            "scheme",
            "host",
            "port",
            "path",
            "query",
            "body",
        ],
    }


@pytest.fixture
def vcr_cassette_name(request):
    """Name of the VCR cassette, changed to {table_name}."""
    test_arguments = request.node.callspec.params
    if "table_name" in test_arguments:
        table_name = test_arguments["table_name"]
        return table_name
    else:
        # Fallback
        test_name = request.node.name
        return test_name
