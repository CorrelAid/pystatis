"""Module contains business logic related to destatis tables."""

import json
from io import StringIO

import pandas as pd

from pystatis import db
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

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def get_data(
        self,
        *,
        prettify: bool = True,
        area: str = "all",
        startyear: str = "",
        endyear: str = "",
        timeslices: str = "",
        regionalvariable: str = "",
        regionalkey: str = "",
        stand: str = "",
        language: str = "de",
        quality: bool = False,
    ):
        """Downloads raw data and metadata from GENESIS-Online.

        Additional keyword arguments are passed on to the GENESIS-Online GET request for tablefile.

        Args:
            prettify (bool, optional): Reformats the table into a readable format. Defaults to True.
            area (str, optional): Area to search for the object in GENESIS-Online. Defaults to "all".
            startyear (str, optional): Data beginning with that year will be returned.
                Parameter is cumulative to `timeslices`. Supports 4 digits (jjjj) or 4+2 digits (jjjj/jj).
                Accepts values between "1900" and "2100".
            endyear (str, optional): Data ending with that year will be returned.
                Parameter is cumulative to `timeslices`. Supports 4 digits (jjjj) or 4+2 digits (jjjj/jj).
                Accepts values between "1900" and "2100".
            timeslices (str, optional): Number of time slices to be returned.
                This parameter is cumulative to `startyear` and `endyear`.
            regionalvariable (str, optional): "code" der Regionalklassifikation (RKMerkmal),
                auf die die Auswahl mittels `regionalkey` angewendet werden soll.
                Accepts 1-6 characters.
            regionalkey (str, optional): Übergabe des Amtlichen Gemeindeschlüssel (AGS).
                Multiple values can be passed as a comma-separated list.
                Accepts 1-8 characters. "*" can be used as wildcard.
            stand (str, optional): Provides table only if it is newer.
                "tt.mm.jjjj hh:mm" or "tt.mm.jjjj". Example: "24.12.2001 19:15".
            language (str, optional): Messages and data descriptions are supplied in this language.
            quality (bool, optional): If True, Value-adding quality labels are issued.
        """
        params = {
            "name": self.name,
            "area": area,
            "startyear": startyear,
            "endyear": endyear,
            "timeslices": timeslices,
            "regionalvariable": regionalvariable,
            "regionalkey": regionalkey,
            "stand": stand,
            "language": language,
            "quality": quality,
            "format": "ffcsv",
        }

        raw_data_bytes = load_data(endpoint="data", method="tablefile", params=params)
        assert isinstance(raw_data_bytes, bytes)  # nosec assert_used
        raw_data_str = raw_data_bytes.decode("utf-8-sig")

        self.raw_data = raw_data_str
        data_buffer = StringIO(raw_data_str)
        self.data = pd.read_csv(data_buffer, sep=";", na_values=["...", ".", "-", "/", "x"])

        if prettify:
            self.data = self.prettify_table(self.data, db.identify_db(self.name)[0])

        metadata = load_data(endpoint="metadata", method="table", params=params)
        metadata = json.loads(metadata)
        assert isinstance(metadata, dict)  # nosec assert_used

        self.metadata = metadata

    @staticmethod
    def prettify_table(data: pd.DataFrame, db_name: str) -> pd.DataFrame:
        """Reformat the data into a more readable table

        Args:
            data (pd.DataFrame): A pandas dataframe created from raw_data
            db_name (str): The name of the database.

        Returns:
            pd.DataFrame: Formatted dataframe that omits all unnecessary Code columns
            and includes informative columns names
        """
        match db_name:
            case "genesis":
                pretty_data = Table.parse_genesis_table(data)
            case "zensus":
                pretty_data = Table.parse_zensus_table(data)
            case "regio":
                pretty_data = Table.parse_regio_table(data)
            case _:
                pretty_data = data

        return pretty_data

    @staticmethod
    def parse_genesis_table(data: pd.DataFrame) -> pd.DataFrame:
        """Parse GENESIS table ffcsv format into a more readable format"""
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
        values.columns = [name.split("__")[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data

    @staticmethod
    def parse_zensus_table(data: pd.DataFrame) -> pd.DataFrame:
        """Parse Zensus table ffcsv format into a more readable format"""
        # Extracts time column with name from first element of Zeit_Label column
        time = pd.DataFrame({data["time_label"].iloc[0]: data["time"]})

        # Extracts new column names from first values of the Merkmal_Label columns
        # and assigns these to the relevant attribute columns (Auspraegung_Label)
        attributes = data.filter(like="variable_attribute_label")
        attributes.columns = data.filter(regex=r"\d+_variable_label").iloc[0].tolist()

        values = pd.DataFrame({data["value_variable_label"].iloc[0]: data["value"]})

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data

    @staticmethod
    def parse_regio_table(data: pd.DataFrame) -> pd.DataFrame:
        """Parse Regionalstatistik table ffcsv format into a more readable format"""
        # Extracts time column with name from first element of Zeit_Label column
        time = pd.DataFrame({data["Zeit_Label"].iloc[0]: data["Zeit"]})

        # Extracts new column names from first values of the Merkmal_Label columns
        # and assigns these to the relevant attribute columns (Auspraegung_Label)
        attributes = data.filter(like="Auspraegung_Label")
        attributes.columns = data.filter(like="Merkmal_Label").iloc[0].tolist()

        # Extracts new column names from first values of the Merkmal_Label columns
        # and assigns these to the relevant code columns (Auspraegung_Code)
        codes = data.filter(like="Auspraegung_Code")
        codes.columns = data.filter(like="Merkmal_Label").iloc[0].tolist()
        codes.columns = [code + "_Code" for code in codes.columns]

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the readable label and omit both the code and the unit
        values.columns = [name.split("__")[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, codes, values], axis=1)
        return pretty_data
