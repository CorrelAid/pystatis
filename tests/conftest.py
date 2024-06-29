import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "filter_query_parameters": ["username", "password"],
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
