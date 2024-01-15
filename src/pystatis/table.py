"""Module contains business logic related to destatis tables."""
from io import StringIO

import pandas as pd

from pystatis.http_helper import load_data


class Table:
    """A wrapper class holding all relevant data and metadata about a given table.

    Args:
        name (str): The unique identifier of this table.
        raw_data (str): The raw tablefile data as returned by the /data/table endpoint.
        data (pd.DataFrame): The parsed data as a pandas data frame.
        metadata (dict): Metadata as returned by the /metadata/table endpoint.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.raw_data = ""
        self.data = pd.DataFrame()
        self.metadata: dict = {}

    def get_data(self, area: str = "all", prettify: bool = True, **kwargs):
        """Downloads raw data and metadata from GENESIS-Online.

        Additional keyword arguments are passed on to the GENESIS-Online GET request for tablefile.

        Args:
            area (str, optional): Area to search for the object in GENESIS-Online. Defaults to "all".
            prettify (bool, optional): Reformats the table into a readable format. Defaults to True.
        """
        params = {"name": self.name, "area": area, "format": "ffcsv"}

        params |= kwargs

        raw_data = load_data(
            endpoint="data", method="tablefile", params=params, as_json=False
        )
        assert isinstance(raw_data, str)  # nosec assert_used
        self.raw_data = raw_data
        data_str = StringIO(raw_data)
        self.data = pd.read_csv(data_str, sep=";")
        if prettify:
            self.data = self.prettify_table(self.data)

        metadata = load_data(
            endpoint="metadata", method="table", params=params, as_json=True
        )
        assert isinstance(metadata, dict)  # nosec assert_used
        self.metadata = metadata

    @staticmethod
    def prettify_table(data: pd.DataFrame) -> pd.DataFrame:
        """Reformat the data into a more readable table

        Args:
            data (pd.DataFrame): A pandas dataframe created from raw_data

        Returns:
            pd.DataFrame: Formatted dataframe that omits all unnecessary Code columns
            and includes informative columns names
        """
        # Extracts time column with name from first element of Zeit_Label column
        time = pd.DataFrame({data["Zeit_Label"].iloc[0]: data["Zeit"]})

        # Extracts new column names from first values of the Merkmal_Label columns
        # and assigns these to the relevant attribute columns (Auspraegung_Label)
        attributes = data.filter(like="Auspraegung_Label")
        attributes.columns = data.filter(like="Merkmal_Label").iloc[0].tolist()

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the readable label and omit both the code and the unit
        values.columns = [
            " ".join(name.split("_")[1:-1]) for name in values.columns
        ]

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data
