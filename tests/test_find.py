import pandas as pd
import pytest

from pystatis.find import Find, Results


def test_get_code_with_valid_row_numbers():
    # Happy path test for get_code() method with valid list of row numbers
    _list = ["A", "B", "C"]
    df = pd.DataFrame(
        {"Code": _list, "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "tables")
    assert results.get_code([0, 2]) == [_list[i] for i in [0, 2]]


def test_init_with_empty_dataframe():
    # Edge case test for Results object creation with empty pd.DataFrame
    df = pd.DataFrame()
    category = "tables"

    # Execution
    results = Results(df, category)

    # Assertion
    assert isinstance(results, Results)
    assert isinstance(results.df, pd.DataFrame)
    assert results.category == category


def test_get_code_with_empty_row_numbers():
    # Edge case test for get_code() method with empty list of row numbers
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )

    # Execution
    results = Results(df, "tables")

    # Assertion
    assert results.get_code([]) == []


def test_get_metadata_with_empty_row_numbers(mocker, capsys):
    # Edge case test for get_metadata() method with empty list of row numbers
    data = {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    df = pd.DataFrame(data)
    category = "tables"
    results = Results(df, category)
    mocker.patch.object(results, "_get_metadata_results")

    # Execution
    results.get_metadata([])
    captured = capsys.readouterr()

    # Assertion
    assert captured.out == ""


def test_get_metadata_tables_with_valid_row_numbers(mocker, capsys):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "tables")
    mocker.patch.object(
        results,
        "_get_metadata_results",
        return_value={
            "Object": {
                "Structure": {
                    "Head": {"Content": "Table A"},
                    "Columns": [
                        {"Content": "Column 1"},
                        {"Content": "Column 2"},
                    ],
                    "Rows": [{"Content": "Row 1"}, {"Content": "Row 2"}],
                }
            }
        },
    )

    # Execution
    results.get_metadata([0])
    captured = capsys.readouterr()

    # Assertion
    assert (
        captured.out
        == f"TABLES A - 0\nName:\nTable A\n{'-' * 20}\nColumns:\nColumn 1\nColumn 2\n{'-' * 20}\nRows:\nRow 1\nRow 2\n{'-' * 40}\n"
    )


def test_get_metadata_cubes_with_valid_row_numbers(mocker, capsys):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "cubes")
    mocker.patch.object(
        results,
        "_get_metadata_results",
        return_value={
            "Object": {
                "Content": "Table A",
                "Structure": {"Axis": [{"Content": "Table A"}]},
            }
        },
    )

    # Execution
    results.get_metadata([0])
    captured = capsys.readouterr()

    # Assertion
    assert (
        captured.out
        == f"CUBES A - 0\nName:\nTable A\n{'-' * 20}\nContent:\nTable A\n{'-' * 40}\n"
    )


def test_get_metadata_statistics_with_valid_row_numbers(mocker, capsys):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "statistics")
    mocker.patch.object(
        results,
        "_get_metadata_results",
        return_value={
            "Object": {
                "Content": "Table A",
                "Cubes": "Cube A",
                "Variables": "Variable A",
                "Updated": "Updated A",
            }
        },
    )

    # Execution
    results.get_metadata([0])
    captured = capsys.readouterr()

    # Assertion
    assert (
        captured.out
        == f"STATISTICS A - 0\nName:\nTable A\n{'-' * 20}\nContent:\nCube A Cubes\nVariable A Variables\nUpdated A Updated\n{'-' * 40}\n"
    )


def test_get_metadata_variables_with_valid_row_numbers(mocker, capsys):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "variables")
    mocker.patch.object(
        results,
        "_get_metadata_results",
        return_value={
            "Object": {"Content": "Table A", "Information": "Information A"}
        },
    )

    # Execution
    results.get_metadata([0])
    captured = capsys.readouterr()

    # Assertion
    assert (
        captured.out
        == f"VARIABLES A - 0\nName:\nTable A\n{'-' * 20}\nInformation:\nInformation A\n{'-' * 40}\n"
    )


def test_get_metadata_wrong_category(mocker):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    category = "category"
    results = Results(df, category)
    mocker.patch.object(results, "_get_metadata_results", return_value={})

    # Execution & Assertion
    with pytest.raises(ValueError):
        results.get_metadata([0])


def test__get_metadata_results(mocker):
    # Setup
    df = pd.DataFrame(
        {"Code": ["A", "B", "C"], "Name": ["Table A", "Table B", "Table C"]}
    )
    results = Results(df, "variables")
    mocker.patch("pystatis.find.load_data", return_value={})

    # Execution
    response = results._get_metadata_results("category", "code")

    # Assertion
    assert response == {}


def test_summary_empty_results():
    # Setup
    query = "test"
    find_obj = Find(query)

    # Exercution
    summary = find_obj.summary()

    # Assertion
    assert isinstance(summary, str)
    assert "No data found" in summary


def test_run_returns_summary(mocker, capsys):
    # Setup
    query = "test"
    find_obj = Find(query)
    mocker.patch(
        "pystatis.find.load_data",
        return_value={
            "Statistics": {},
            "Variables": {},
            "Tables": {},
            "Cubes": {},
        },
    )

    # Execution
    find_obj.run()
    captured = capsys.readouterr()

    # Assertion
    assert (
        captured.out
        == f"##### Results #####\n{'-' * 40}\n# Number of tables: 0\n# Preview:\n\n{'-' * 40}\n# Number of statistics: 0\n# Preview:\n\n{'-' * 40}\n# Number of variables: 0\n# Preview:\n\n{'-' * 40}\n# Number of cubes: 0\n# Preview:\n\n{'-' * 40}\n# Use object.tables, object.statistics, object.variables or object.cubes to get all results.\n{'-' * 40}\n"
    )
