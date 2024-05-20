"""Module contains business logic related to destatis tables."""

import json
import re
from io import StringIO

import pandas as pd

from pystatis import db
from pystatis.config import COLUMN_NAME_DICT
from pystatis.exception import QueryParameterError
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

        if language not in ["de", "en"]:
            raise QueryParameterError(f"Language {language} is not supported. Please choose from: ['de', 'en'].")

        raw_data_bytes = load_data(endpoint="data", method="tablefile", params=params)
        assert isinstance(raw_data_bytes, bytes)  # nosec assert_used
        raw_data_str = raw_data_bytes.decode("utf-8-sig")

        self.raw_data = raw_data_str
        # sometimes the data contains invalid rows that do not start with the statistics number (always first column)
        # so we have to do this workaround to get a proper data frame later
        raw_data_lines = raw_data_str.splitlines(keepends=True)
        raw_data_header = raw_data_lines[0]
        raw_data_str = raw_data_header + "".join(line for line in raw_data_lines[1:] if line[:4].isdigit())
        data_buffer = StringIO(raw_data_str)

        decimal_char = "," if language == "de" else "."
        self.data = pd.read_csv(
            data_buffer,
            sep=";",
            na_values=["...", ".", "-", "/", "x"],
            decimal=decimal_char,
        )

        if prettify:
            self.data = self.prettify_table(
                data=self.data,
                db_name=db.identify_db(self.name)[0],
                language=language,
            )

        metadata = load_data(endpoint="metadata", method="table", params=params)
        metadata = json.loads(metadata)
        assert isinstance(metadata, dict)  # nosec assert_used

        self.metadata = metadata

    @staticmethod
    def prettify_table(data: pd.DataFrame, db_name: str, language: str) -> pd.DataFrame:
        """Reformat the data into a more readable table

        Args:
            data (pd.DataFrame): A pandas dataframe created from raw_data
            db_name (str): The name of the database.
            language (str): The requested language. One of "de" or "en".

        Returns:
            pd.DataFrame: Formatted dataframe that omits all unnecessary Code columns
            and includes informative columns names
        """
        match db_name:
            case "genesis":
                pretty_data = Table.parse_genesis_table(data, language)
            case "zensus":
                pretty_data = Table.parse_zensus_table(data, language)
            case "regio":
                pretty_data = Table.parse_regio_table(data, language)
            case _:
                pretty_data = data

        return pretty_data

    @staticmethod
    def parse_genesis_table(data: pd.DataFrame, language: str) -> pd.DataFrame:
        """Parse GENESIS table ffcsv format into a more readable format"""

        column_name_dict = COLUMN_NAME_DICT["genesis-regio"][language]

        # Extracts time column with name from last element of Zeit_Label column
        time = pd.DataFrame({data[column_name_dict["time_label"]].iloc[-1]: data[column_name_dict["time"]]})

        # Extracts new column names from last values of the variable label columns
        # and assigns these to the relevant attribute columns (variable level)
        attributes = data.filter(like=column_name_dict["value_label"])
        attributes.columns = data.filter(like=column_name_dict["variable_label"]).iloc[-1].tolist()

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the label and the unit and omits the code
        values.columns = [re.split(r"_{2,}", name, maxsplit=1)[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, values], axis=1).dropna(axis=0, how="all")
        return pretty_data

    @staticmethod
    def parse_zensus_table(data: pd.DataFrame, language: str) -> pd.DataFrame:
        """Parse Zensus table ffcsv format into a more readable format"""
        # TODO: add distinction between languages.
        column_name_dict = COLUMN_NAME_DICT["zensus"][language]

        # add the unit to the column names for the value columns
        data[column_name_dict["value_variable_label"]] = data[column_name_dict["value_variable_label"]].str.cat(
            data[column_name_dict["value_unit"]], sep="__"
        )

        pivot_table = data.pivot(
            index=data.columns[:-4].to_list(),
            columns=column_name_dict["value_variable_label"],
            values=column_name_dict["value"],
        )
        value_columns = pivot_table.columns.to_list()
        pivot_table.reset_index(inplace=True)
        pivot_table.columns.name = None

        time_label = data[column_name_dict["time_label"]].iloc[0]
        time = pd.DataFrame({time_label: pivot_table[column_name_dict["time"]]})

        attributes = pivot_table.filter(regex=r"\d+_" + column_name_dict["variable_attribute_label"])
        attributes.columns = pivot_table.filter(regex=r"\d+_" + column_name_dict["variable_label"]).iloc[0].tolist()

        pretty_data = pd.concat([time, attributes, pivot_table[value_columns]], axis=1)

        return pretty_data

    @staticmethod
    def parse_regio_table(data: pd.DataFrame, language: str) -> pd.DataFrame:
        """Parse Regionalstatistik table ffcsv format into a more readable format"""

        column_name_dict = COLUMN_NAME_DICT["genesis-regio"][language]

        # Extracts time column with name from last element of Zeit_Label column
        time = pd.DataFrame({data[column_name_dict["time_label"]].iloc[-1]: data[column_name_dict["time"]]})

        # Extracts new column names from first values of the Merkmal_Label columns
        # and assigns these to the relevant attribute columns (Auspraegung_Label)
        attributes = data.filter(like=column_name_dict["value_label"])
        attributes.columns = data.filter(like=column_name_dict["variable_label"]).iloc[0].tolist()

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the label and the unit and omit the code
        values.columns = [re.split(r"_{2,}", name, maxsplit=1)[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data
