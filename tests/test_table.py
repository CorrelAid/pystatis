import pandas as pd
import pytest

import pystatis


@pytest.mark.vcr(filter_query_parameters=["username", "password"])
@pytest.mark.parametrize("table_name", ["12211-0001"])
def test_get_data(table_name: str):
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False)
    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty
    assert isinstance(table.raw_data, str)
    assert table.raw_data != ""


@pytest.mark.vcr(filter_query_parameters=["username", "password"])
@pytest.mark.parametrize("table_name", ["12211-0001"])
def test_prettify(table_name):
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True)
    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty
