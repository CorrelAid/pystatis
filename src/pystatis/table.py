"""Module contains business logic related to destatis tables."""

import json
import warnings
from io import StringIO

import pandas as pd

from pystatis import config, db
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
        # special values mapping
        self.mapping_de = {
            "0": "weniger als die Hälfte von 1 in der letzten besetzten Stelle, jedoch mehr als nichts",
            "-": "nichts vorhanden",
            "...": "Angabe fällt später an",
            "/": "keine Angaben, da Zahlenwert nicht sicher genug",
            ".": "Zahlenwert unbekannt oder geheimzuhalten",
            "x": "Tabellenfach gesperrt, weil Aussage nicht sinnvoll",
            "()": "Aussagewert eingeschränkt, da der Zahlenwert statistisch relativ unsicher ist",
            "p": "vorläufige Zahl",
            "r": "berichtigte Zahl",
            "s": "geschätzte Zahl",
            "e": "endgültige Zahl",
        }
        self.mapping_en = {
            "0": "less than half of 1 in the last occupied place, but more than nothing",
            "-": "not available",
            "...": "information will be available later",
            "/": "no information because the numerical value is not certain enough",
            ".": "numerical value unknown or to be kept secret",
            "x": "table compartment locked because statement is not meaningful",
            "()": "statement value restricted because the numerical value is statistically relatively uncertain",
            "p": "preliminary number",
            "r": "corrected number",
            "s": "estimated number",
            "e": "final number",
        }

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
            "format": "ffcsv",
        }
        if quality:
            params["quality"] = "on"

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
        # let pandas handle automatic type conversion and only handle edge case columns with known leading zeros
        leading_zeros_cols = config.ZENSUS_AGS_CODES + config.REGIO_AGS_CODES
        leading_zeros_dict = {key: "str" for key in leading_zeros_cols}
        self.data = pd.read_csv(data_buffer, sep=";", dtype=leading_zeros_dict, na_values=["...", ".", "-", "/", "x"])

        # mapping of special values to their meaning
        if language == "de":
            mapping = self.mapping_de
        elif language == "en":
            mapping = self.mapping_en
        else:
            # TODO: is this required? error should probably already be triggered by the http_helper/ request
            raise ValueError(f"Language {language} is not supported.")

        # Add a quality column for each column in the data frame if the column contains special values
        for column in self.data.columns:
            # try to convert data to numeric type
            try:
                self.data[column] = pd.to_numeric(self.data[column], errors="ignore")
            except ValueError:
                # try German decimal separator
                try:
                    self.data[column] = self.data[column].str.replace(",", ".").astype(float)
                except ValueError:
                    pass

            if column.endswith("__q"):
                # replace the special values with their meaning (? up for discussion)
                self.data[column] = self.data[column].astype(str)
                self.data[column].replace(mapping, inplace=True)

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
        # extracts the label and the unit and omit the code
        values.columns = [name.split("__", maxsplit=1)[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data

    @staticmethod
    def parse_zensus_table(data: pd.DataFrame) -> pd.DataFrame:
        """Parse Zensus table ffcsv format into a more readable format"""
        # add the unit to the column names for the value columns
        data["value_variable_label"] = data["value_variable_label"].str.cat(data["value_unit"], sep="__")

        if "value_q" in data.columns:
            data = data.drop(columns=["value_q"])
            warnings.warn("Quality columns are not supported for Zensus tables.", UserWarning)

        pivot_table = data.pivot(index=data.columns[:-4].to_list(), columns="value_variable_label", values="value")
        value_columns = pivot_table.columns.to_list()
        pivot_table.reset_index(inplace=True)
        pivot_table.columns.name = None

        time_label = data["time_label"].iloc[0]
        time = pd.DataFrame({time_label: pivot_table["time"]})

        attributes = pivot_table.filter(regex=r"\d+_variable_attribute_label")
        attributes.columns = pivot_table.filter(regex=r"\d+_variable_label").iloc[0].tolist()

        pretty_data = pd.concat([time, attributes, pivot_table[value_columns]], axis=1)

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

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the label and the unit and omit the code
        values.columns = [name.split("__", maxsplit=1)[1] for name in values.columns]

        pretty_data = pd.concat([time, attributes, values], axis=1)
        return pretty_data
