"""Implements find endpoint to retrieve results based on query"""

import json
from typing import Any

import pandas as pd

from pystatis.http_helper import load_data
from pystatis.results import Results

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


class Find:
    """
    A class representing the find object that includes Result objects for variables, statistics, cubes and tables.

    Attributes:
        query (str): The query that is provided to find endpoint.
        db_name (str): The database that is used for the query.
            One of "genesis", "zensus", "regio".
        statistics (Results): Statistics that match with the query.
        tables (Results): Tables that match with the query.
        variables (Results): Variables that match with the query.
        cubes (Results): Cubes that match with the query.

    Methods:
        run(): Queries the API and prints summary.
        summary(): Prints summary of all results.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, query: str, db_name: str, top_n_preview: int = 5) -> None:
        """Method for retrieving data from find endpoint.

        Args:
            query (str): The query that is provided to find endpoint.
            db_name (str): The database that is used for the query.
                One of "genesis", "zensus", "regio".
            top_n_preview (int): Number of previews in print summary.
        """
        self.query = query
        self.db_name = db_name

        self.top_n_preview = top_n_preview
        self.statistics = Results(pd.DataFrame(), "statistics", db_name)
        self.variables = Results(pd.DataFrame(), "variables", db_name)
        self.tables = Results(pd.DataFrame(), "tables", db_name)
        self.cubes = Results(pd.DataFrame(), "cubes", db_name)

        self.is_run = False

    def run(self) -> None:
        """
        Execute the search to find statistics, variables, tables and cubes.
        """
        self.statistics = self._get_find_results("statistics")
        self.variables = self._get_find_results("variables")
        self.tables = self._get_find_results("tables")
        self.cubes = self._get_find_results("cubes")

        self.is_run = True

        print(self.summary())

    def summary(self) -> str:
        """
        Returns:
            str: String that contains summary statistics.
        """

        if self.is_run:
            return "\n".join(
                [
                    "##### Results #####",
                    f"{'-' * 40}",
                    f"# Number of tables: {len(self.tables.df)}",
                    "# Preview:",
                    self.tables.df.iloc[: self.top_n_preview].to_markdown(),
                    f"{'-' * 40}",
                    f"# Number of statistics: {len(self.statistics.df)}",
                    "# Preview:",
                    self.statistics.df.iloc[: self.top_n_preview].to_markdown(),
                    f"{'-' * 40}",
                    f"# Number of variables: {len(self.variables.df)}",
                    "# Preview:",
                    self.variables.df.iloc[: self.top_n_preview].to_markdown(),
                    f"{'-' * 40}",
                    f"# Number of cubes: {len(self.cubes.df)}",
                    "# Preview:",
                    self.cubes.df.iloc[: self.top_n_preview].to_markdown(),
                    f"{'-' * 40}",
                    "# Use object.tables, object.statistics, object.variables or object.cubes to get all results.",
                    f"{'-' * 40}",
                ]
            )
        else:
            return "No data found. Please use .run() to retrieve data."

    def _get_find_results(self, category: str, **kwargs: Any) -> "Results":
        """
        Based on the query (term), category and additional query parameters a Result object will be created.

        Args:
            category (str): Category of the result. E.g. "tables", "cubes"
            query_params (dict, optional): Additional query parameters (Default: None)
        Returns:
            pd.DataFrame
        """

        params = {
            "term": self.query,
            "category": category,
        }

        params |= kwargs

        response = load_data(
            endpoint="find",
            method="find",
            params=params,
            db_name=self.db_name,
        )
        response = json.loads(response)
        assert isinstance(response, dict)  # nosec assert_used
        response_dict = response[category.capitalize()]
        response_df = pd.DataFrame(response_dict).replace("\n", " ", regex=True)

        return Results(response_df, category, db_name=self.db_name)
