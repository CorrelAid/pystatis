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

    def get_data(self, area: str = "all", **kwargs):
        """Downloads raw data and metadata from GENESIS-Online.

        Additional keyword arguments are passed on to the GENESIS-Online GET request for tablefile.

        Args:
            area (str, optional): Area to search for the object in GENESIS-Online. Defaults to "all".
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
        self.nice_data = format_table(self.data)

        metadata = load_data(
            endpoint="metadata", method="table", params=params, as_json=True
        )
        assert isinstance(metadata, dict)  # nosec assert_used
        self.metadata = metadata

def format_table(data: pd.DataFrame, 
                ) -> pd.DataFrame:
    """Format the raw data into a more readable table
    
    Args:
        data (pd.DataFrame): A pandas dataframe created with get_data()
    
    Returns:
        pd.DataFrame: Formatted dataframe that omits all CODE columns and gives 
        informative columns names.
    """
    time_name, = data["Zeit_Label"].unique()
    time_values = data["Zeit"]

    merkmal_labels = data.filter(like="Merkmal_Label").columns
    indep_names = [data[name].unique()[0] for name in merkmal_labels] # list of column names from Merkmal_Label

    auspraegung_labels = data.filter(like="Auspraegung_Label").columns
    indep_values = [data[name] for name in auspraegung_labels] # list of data from Ausgepragung_Label

    dep_values = data.loc[:,auspraegung_labels[-1]:].iloc[:,1:] # get all columns after last Auspraegung column
    dep_names = [" ".join(name.split('_')[1:]) 
                    for name in dep_values.columns] # splits strings in column names for readability

    nice_dict = {time_name:time_values, 
                    **dict(zip(indep_names, indep_values)), 
                    **dict(zip(dep_names, dep_values.values.T))}
    nice_data = pd.DataFrame(nice_dict)
    return nice_data