"""Module contains business logic related to destatis tables."""

import json
import re
from io import StringIO
from typing import Any

import numpy as np
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
        self.metadata: dict[str, Any] = {}

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
        quality: str = "off",
    ) -> None:
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
            regionalvariable (str, optional): "code" of the regional classification (RKMerkmal),
                to which the selection using `regionalkey` is to be applied.
                Accepts 1-6 characters.
                Possible values:

                - Regionalstatistik (only for tables ending with "B", see /catalogue/variables):
                    - "DG" (Deutschland, 1) -> will not return extra column
                    - "DLAND" (Bundesländer, 16)
                    - "REGBEZ" (Regierungsbezirke, 44)
                    - "KREISE" (Kreise und kreisfreie Städte, 489)
                    - "GEMEIN" (Gemeinden, 13564)
                - Zensusdatenbank (for all tables, see /catalogue/variables):
                    - "GEODL1" (Deutschland, 1) -> will not return extra column
                    - "GEODL3" (Deutschland, 1) -> will not return extra column
                    - "GEOBL1" (Bundesländer, 16)
                    - "GEOBL3" (Bundesländer, 16)
                    - "GEOBZ1" (Bezirke (Hamburg und Berlin), 19)
                    - "GEOGM1" (Gemeinden, 11340)
                    - "GEOGM2" (Gemeinden mit min. 10_000 Einwohnern, 1574)
                    - "GEOGM3" (Gemeinden mit min. 10_000 Einwohnern, 1574)
                    - "GEOGM4" (Gemeinden (Gebietsstand 15.05.2022), 10787)
                    - "GEOLK1" (Landkreise und kreisfreie Städte, 412)
                    - "GEOLK3" (Landkreise und kreisfreie Städte, 412)
                    - "GEOLK4" (Landkreise u. krsfr. Städte (Stand 15.05.22), 400)
                    - "GEORB1" (Regierungsbezirke/Statistische Regionen, 36)
                    - "GEORB3" (Regierungsbezirke/Statistische Regionen, 36)
                    - "GEOVB1" (Gemeindeverbände, 1333)
                    - "GEOVB2" (Gemeindeverbände mit mindestens 10 000 Einwohnern, 338)
                    - "GEOVB3" (Gemeindeverbände mit mindestens 10 000 Einwohnern, 157)
                    - "GEOVB4" (Gemeindeverbände (Gebietsstand 15.05.2022), 1207)
            regionalkey (str, optional): Official municipality key (AGS).
                Multiple values can be passed as a comma-separated list.
                Accepts 1-12 characters. "*" can be used as wildcard.
            stand (str, optional): Only download the table if it is newer than the status date.
                "tt.mm.jjjj hh:mm" or "tt.mm.jjjj". Example: "24.12.2001 19:15".
            language (str, optional): Messages and data descriptions are supplied in this language.
                For GENESIS and Zensus, ['de', 'en'] are supported. For Regionalstatistik, only 'de' is supported.
            quality (str): One of "on" or "off". If "on", quality symbols are part of the download and
                additional columns (__q) are displayed. Defaults to "off".
                The explanation of the quality labels can be found online after retrieving the table values,
                table -> explanation of symbols or at e.g.
                https://www-genesis.destatis.de/genesis/online?operation=ergebnistabelleQualitaet&language=en&levelindex=3&levelid=1719342760835#abreadcrumb.
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

        db_matches = db.identify_db_matches(self.name)
        db_name = db.select_db_by_credentials(db_matches)
        db_version = config.VERSION_MAPPING[db_name]

        raw_data_bytes = load_data(
            endpoint="data", method="tablefile", params=params, db_name=db_name
        )
        assert isinstance(raw_data_bytes, bytes)  # nosec assert_used
        raw_data_str = raw_data_bytes.decode("utf-8-sig")

        self.raw_data = raw_data_str

        # sometimes the data contains invalid rows that do not start with the statistics number (always first column)
        # so we have to do this workaround to get a proper data frame later
        raw_data_lines = raw_data_str.splitlines(keepends=True)
        raw_data_header = raw_data_lines[0]
        raw_data_str = raw_data_header + "".join(
            line for line in raw_data_lines[1:] if line[:4].isdigit()
        )
        data_buffer = StringIO(raw_data_str)

        # find AGS column, if present, to set dtype correctly and avoid mixed types
        ags_codes = (
            config.ZENSUS_AGS_CODES
            if db_name == "zensus"
            else config.REGIO_AND_GENESIS_AGS_CODES
        )
        pos_of_ags_col = np.where(
            pd.Series(raw_data_lines[1].split(";")).isin(ags_codes)
        )[0]

        self.data = pd.read_csv(
            data_buffer,
            sep=";",
            na_values=["...", ".", "-", "/", "x"],
            decimal="," if language == "de" else ".",
            dtype={raw_data_header.split(";")[pos + 2]: str for pos in pos_of_ags_col},
            parse_dates=[config.LANG_TO_COL_MAPPING[db_version][language]["time"]],
            date_format="%d.%m.%Y" if language == "de" else "%Y-%m-%d",
        )

        if prettify:
            self.data = self.prettify_table(
                data=self.data,
                db_name=db.identify_db_matches(self.name)[0],
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
            case "regio":
                pretty_data = Table.parse_v4_table(data, language)
            case "genesis" | "zensus":
                pretty_data = Table.parse_v5_table(data, db_name, language)
            case _:
                pretty_data = data

        return pretty_data

    @staticmethod
    def parse_v4_table(data: pd.DataFrame, language: str) -> pd.DataFrame:
        """
        Parse ffcsv format for tables from GENESIS and Regionalstatistik into a more readable format
        """

        column_name_dict = config.LANG_TO_COL_MAPPING["v4"][language]
        time_col = column_name_dict["time"]
        time_label_col = column_name_dict["time_label"]
        variable_label_col = column_name_dict["variable_label"]
        value_label_col = column_name_dict["value_label"]
        ags_label_col = config.ARS_OR_AGS_MAPPING["regio"][language]

        # Extracts time column with name from last element of Zeit_Label column
        time = pd.DataFrame({data[time_label_col].iloc[-1]: data[time_col]})

        # Whenever there is a column with a regional code, we add this column to the final output
        # As the position is unknown, we have to identify this column by looking for the AGS code
        ags_codes = list(
            set(config.REGIO_AND_GENESIS_AGS_CODES) - set(config.EXCLUDE_AGS_CODES)
        )
        pos_of_ags_col, ags_code = Table.extract_ags_col(data, ags_codes, ags_label_col)

        # Extracts new column names from last values of the variable label columns
        # and assigns these to the relevant attribute columns (variable level)
        attributes = data.filter(like=value_label_col)
        attributes.columns = data.filter(like=variable_label_col).iloc[-1].tolist()

        # Selects all columns containing the values
        values = data.filter(like="__")

        # Given a name like BEV036__Bevoelkerung_in_Hauptwohnsitzhaushalten__1000
        # extracts the label and the unit and omits the code
        values.columns = [
            re.split(r"_{2,}", name, maxsplit=1)[1] for name in values.columns
        ]

        # remove single "_" between words in values.columns but keep "__" as separator
        values.columns = [
            name.split("__")[0].replace("_", " ") + "__" + name.split("__")[1]
            for name in values.columns
        ]

        pretty_data = pd.concat([time, attributes, values], axis=1).dropna(
            axis=0, how="all"
        )
        if ags_code is not None:
            # Genesis has always the same time attribute as first column,
            # and each attribute always has 4 columns so pos_of_ags_col // 4
            # adjusts the original counter to the shorter column list of pretty_data
            pretty_data.insert(
                loc=pos_of_ags_col // 4, column=ags_code.name, value=ags_code
            )

        return pretty_data

    @staticmethod
    def parse_v5_table(data: pd.DataFrame, db_name: str, language: str) -> pd.DataFrame:
        """Parse Zensus table ffcsv format into a more readable format"""
        column_name_dict = config.LANG_TO_COL_MAPPING["v5"][language]
        # Zensus and Genesis are both now on v5 but Genesis has different regional codes than Zensus
        ars_label_code = config.ARS_OR_AGS_MAPPING[db_name][language]
        time_col = column_name_dict["time"]
        time_label_col = column_name_dict["time_label"]
        value_col = column_name_dict["value"]
        value_q_col = column_name_dict["value_q"]
        value_unit_col = column_name_dict["value_unit"]
        value_variable_label_col = column_name_dict["value_variable_label"]
        variable_attribute_label_col = column_name_dict["variable_attribute_label"]
        variable_label_col = column_name_dict["variable_label"]

        quality = False
        if value_q_col in data.columns:
            quality = True

        # add the unit to the column names for the value columns
        data[value_variable_label_col] = data[value_variable_label_col].str.cat(
            data[value_unit_col].astype(str).fillna("Unknown_Unit"), sep="__"
        )

        if quality:
            # with quality = 'on' we have an additional column value_q
            # to still use pivot table we have to combine value and value_q
            # so we can later split them again
            data[value_col] = [
                [v, q] for v, q in zip(data[value_col], data[value_q_col])
            ]
            data = data.drop(columns=[value_q_col])

        pivot_table = data.pivot(
            index=[
                col
                for col in data.columns
                if col not in data.filter(regex=r"^value").columns
            ],
            columns=value_variable_label_col,
            values=value_col,
        )

        if quality:
            for col in pivot_table.columns:
                pivot_table.insert(
                    pivot_table.columns.to_list().index(col) + 1,
                    col + "__q",
                    pivot_table[col].apply(lambda x: x[1]),
                )
                pivot_table[col] = pivot_table[col].apply(lambda x: x[0])

        value_columns = pivot_table.columns.to_list()
        pivot_table.reset_index(inplace=True)
        pivot_table.columns.name = None

        time_label = data[time_label_col].iloc[0]
        time = pd.DataFrame({time_label: pivot_table[time_col]})

        # If AGS column is present, add it to the final output
        ags_codes = list(
            set(
                config.ZENSUS_AGS_CODES
                if db_name == "zensus"
                else config.REGIO_AND_GENESIS_AGS_CODES
            )
            - set(config.EXCLUDE_AGS_CODES)
        )
        pos_of_ags_col, ags_code = Table.extract_ags_col(
            pivot_table, ags_codes, ars_label_code
        )

        attributes = pivot_table.filter(regex=r"\d+_" + variable_attribute_label_col)
        # avoid taking label from first row
        # as this can contain value for whole Germany
        # even if table is for regional areas
        attributes.columns = (
            pivot_table.filter(regex=r"\d+_" + variable_label_col).iloc[1].tolist()
        )

        pretty_data = pd.concat([time, attributes, pivot_table[value_columns]], axis=1)
        if ags_code is not None:
            # Genesis has always the same time attribute as first column, and
            # each attribute always has 4 columns so pos_of_ags_col // 4
            # adjusts the original counter to the shorter column list of pretty_data
            pretty_data.insert(
                loc=pos_of_ags_col // 4, column=ags_code.name, value=ags_code
            )

        return pretty_data

    @staticmethod
    def extract_ags_col(
        data: pd.DataFrame, codes: list[str], label: str
    ) -> tuple[np.ndarray, pd.Series | None]:
        """Extracts the AGS column from the data if present.

        Args:
            data (pd.DataFrame): The data frame to extract the AGS column from.
            codes (list[str]): The AGS codes to look for in the data.
            label (str): The label of the AGS column.

        Returns:
            pd.Series | None: The AGS column if present, otherwise None.
        """
        ags_code = None
        # don't compare very first row, as it can often be Germany as a summary
        pos_of_ags_col = np.where(data.iloc[1].isin(codes))[0]
        if pos_of_ags_col.size > 0:
            pos_of_ags_col = pos_of_ags_col[0]
            ags_code = pd.Series(
                data=data.iloc[:, pos_of_ags_col + 2], name=label, dtype=str
            )

        return pos_of_ags_col, ags_code
