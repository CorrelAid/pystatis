"""Helper class for find endpoint to get the codes and metadata of the results."""

import json
from typing import Any

import pandas as pd

from pystatis.http_helper import load_data


class Results:
    """
    A class representing the result object of variables, statistics, cubes and tables.

    Attributes:
        df (pd.DataFrame): The DataFrame that contains the data.
        category (str): Category (plural) of the result. E.g. "tables", "cubes".
        db_name (str): The database that is used for the query.
            One of "genesis", "zensus", "regio".

    Methods:
        get_code(): Gets code based on the index of the object.
        get_metadata(): Gets metadata based on the index of the object.
    """

    def __init__(self, result: pd.DataFrame, category: str, db_name: str) -> None:
        """
        Class that contains the results of a find query.

        Args:
            result (pd.DataFrame): Result of a search query.
            category (str): Category of the result. E.g. "tables", "cubes"
            db_name (str): The database that is used for the query.
            One of "genesis", "zensus", "regio".
        """
        self.df = result
        self.category = category
        self.db_name = db_name

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.df.to_markdown())

    def __len__(self) -> int:
        if len(self.df) > 0:
            return len(self.df)
        else:
            return 0

    def get_code(self, row_numbers: list[int]) -> list[str]:
        """
        Returns the code for a given list of tables.

        Args:
            row_numbers (list[int]): A list that contains the row
                numbers from the results objects. This is not the
                object code.

        Returns:
            table codes (list[str]): Contains the corresponding tables codes.
        """

        codes = self.df.iloc[row_numbers]["Code"]
        return list(codes)

    def show_metadata(self, row_numbers: list[int]) -> None:
        """
        Prints meta data for a given list of tables.

        Args:
            row_numbers (list[int]): A list that contains the
                row_numbers from the results objects.
                This is not the object code.
        """
        codes = self.df.iloc[row_numbers]["Code"]

        for code, ix in zip(codes, row_numbers):
            response = self._get_metadata_results(
                self.category[0:-1], code, self.db_name
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
                        "\n".join([col["Content"] for col in structure_dict["Columns"]]),
                        f"{'-' * 20}",
                        "Rows:",
                        "\n".join([row["Content"] for row in structure_dict["Rows"]]),
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
                        "\n".join([content["Content"] for content in axis_dict]),
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
            else:
                output = ""

            print(output)

    @staticmethod
    def _get_metadata_results(category: str, code: str, db_name: str) -> dict[str, Any]:
        """
        Based on the category and code query parameters the metadata will be generated.

        Args:
            category (str): Category of the result. E.g. "tables", "cubes"
            code (str): The code (identifier) of the relevant category object.
            db_name (str): The database that is used for the query.
                One of "genesis", "zensus", "regio".
        Returns:
            response (json): The response as a json.
        """
        params = {
            "name": code,
        }

        response = load_data(
            endpoint="metadata",
            method=category,
            params=params,
            db_name=db_name,
        )
        response = json.loads(response)
        assert isinstance(response, dict)  # nosec assert_used

        return response
