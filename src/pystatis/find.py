"""Implements find endpoint to retrieve results based on query"""
import pandas as pd

from pystatis.http_helper import load_data

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


class Results:
    """
    A class representing the result object of variables, statistics, cubes and tables.

    Attributes:
        df (pd.DataFrame): The DataFrame that contains the data.
        category (str): Category (plural) of the result. E.g. "tables", "cubes".

    Methods:
        get_code(): Gets code based on the index of the object.
        get_metadata(): Gets metadata based on the index of the object.
    """

    def __init__(self, result: pd.DataFrame, category: str) -> None:
        """
        Class that contains the results of a find query.

        Args:
            result (pd.DataFrame): Result of a search query.
            category (str): Category of the result. E.g. "tables", "cubes"
        """
        self.df = result
        self.category = category

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.df.to_markdown())

    def __len__(self) -> int:
        if len(self.df) > 0:
            return len(self.df)
        else:
            return 0

    def get_code(self, row_numbers: list) -> list:
        """
        Returns the code for a given list of tables.

        Args:
             row_numbers (list): A list that contains the row numbers from the results objects. This is not the object
             code."
        Returns:
             table codes (list): Contains the corresponding tables codes.
        """

        codes = self.df.iloc[row_numbers]["Code"]
        return list(codes)

    def get_metadata(self, row_numbers: list) -> None:
        """
        Prints meta data for a given list of tables.

        Args:
              row_numbers (list): A list that contains the row_numbers from the results objects. This is not the object
              code."
        """
        codes = self.df.iloc[row_numbers]["Code"]

        for code, ix in zip(codes, row_numbers):
            response = self._get_metadata_results(
                self.category[0:-1], code
            )  # Category is truncated, because
            # metadata endpoints works with singulars

            if self.category == "tables":
                structure_dict = response["Object"]["Structure"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        structure_dict["Head"]["Content"],
                        f"{'-' * 20}",
                        "Columns:",
                        "\n".join(
                            [
                                col["Content"]
                                for col in structure_dict["Columns"]
                            ]
                        ),
                        f"{'-' * 20}",
                        "Rows:",
                        "\n".join(
                            [row["Content"] for row in structure_dict["Rows"]]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "cubes":
                axis_dict = response["Object"]["Structure"]["Axis"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        response["Object"]["Content"],
                        f"{'-' * 20}",
                        "Content:",
                        "\n".join(
                            [content["Content"] for content in axis_dict]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "statistics":
                structure_dict = response["Object"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        response["Object"]["Content"],
                        f"{'-' * 20}",
                        "Content:",
                        "\n".join(
                            [
                                f"{structure_dict[content]} {content}"
                                for content in ["Cubes", "Variables", "Updated"]
                            ]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "variables":
                object_dict = response["Object"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        object_dict["Content"],
                        f"{'-' * 20}",
                        "Information:",
                        str(object_dict["Information"]),
                        f"{'-' * 40}",
                    ]
                )

            print(output)

    @staticmethod
    def _get_metadata_results(category: str, code: str) -> dict:
        """
        Based on the category and code query parameters the metadata will be generated.

        Args:
            category (str): Category of the result. E.g. "tables", "cubes"
            code (str): The code (identifier) of the relevant category object.
        Returns:
            response (json): The response as a json.
        """
        params = {
            "name": code,
        }

        response = load_data(
            endpoint="metadata", method=category, params=params, as_json=True
        )
        assert isinstance(response, dict)  # nosec assert_used

        return response


class Find:
    """
    A class representing the find object that includes Result objects for variables, statistics, cubes and tables.

    Attributes:
        query (str): The query that is provided to find endpoint.
        statistics (Results): Statistics that match with the query.
        tables (Results): Tables that match with the query.
        variables (Results): Variables that match with the query.
        cubes (Results): Cubes that match with the query.

    Methods:
        run(): Queries the API and prints summary.
        summary(): Prints summary of all results.
    """

    def __init__(self, query: str, top_n_preview: int = 5) -> None:
        """Method for retrieving data from find endpoint.

        Args:
            query (str): The query that is provided to find endpoint.
            top_n_preview (int): Number of previews in print summary.
        """
        self.query = query

        self.top_n_preview = top_n_preview
        self.statistics = Results(pd.DataFrame(), "statistics")
        self.variables = Results(pd.DataFrame(), "variables")
        self.tables = Results(pd.DataFrame(), "tables")
        self.cubes = Results(pd.DataFrame(), "cubes")

        self.is_run = False

    def run(self):
        self.statistics = self._get_find_results("statistics")
        self.variables = self._get_find_results("variables")
        self.tables = self._get_find_results("tables")
        self.cubes = self._get_find_results("cubes")

        self.is_run = True

        print(self.summary())

    def summary(self):
        """
        Returns:
            summary_string: String that contains summary statistics.
        """

        if self.is_run:
            return "\n".join(
                [
                    "##### Results #####",
                    f"{'-' * 40}",
                    f"# Number of tables: {len(self.tables.df)}",
                    "# Preview:",
                    self.tables.df.iloc[: self.top_n_preview].to_markdown(),
                    f"{'-' * 40}"
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

    def _get_find_results(self, category: str, **kwargs) -> Results:
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
            endpoint="find", method="find", params=params, as_json=True
        )
        assert isinstance(response, dict)  # nosec assert_used
        response_dict = response[category.capitalize()]
        response_df = pd.DataFrame(response_dict).replace("\n", " ", regex=True)

        return Results(response_df, category)
