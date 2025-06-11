"""Module contains business logic related to destatis tables."""

import json
from io import StringIO
from typing import Any

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
        compress: bool = True,
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
            compress (bool, optional): Suppresses empty rows and columns.
                Will reduce table size and thus can help avoid creating jobs. Defaults to True.
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
                Can be used with any table that uses a regional attribute.

                The following attribute codes are handled by `pystatis` by adding an extra column for the official municipality key (AGS):

                - GENESIS-Online (for all tables, see /catalogue/variables):
                    - "DLAND" (Bundesländer, 16)
                    - "DINSG" (Deutschland insgesamt, 1) -> will not return extra AGS column
                    - "DLANDR" (Bundesländer mit Restposition, 17)
                    - "DLANDS" (Bundesländer mit Seehäfen, 6)
                    - "DLANDU" (Bundesländer und Ausland, 17)
                    - "DLANDX" (Bundesländer mit Ausland und Restposition, 18)
                    - "KREISE" (Kreise, 476)
                    - "REGBEZ" (Regierungsbezirke, 38)

                - Regionalstatistik (only for tables ending with "B", see /catalogue/variables):
                    - "DG" (Deutschland, 1) -> will not return ARS column
                    - "DINSG" (Deutschland räumlich insgesamt, 1) -> will not return ARS column
                    - "DLAND" (Bundesländer, 16)
                    - "DLANDU" Bundesländer, 19)
                    - "FAMTGEM" (Gemeinden und Gemeindeverbände, 12779)
                    - "FDINSG" (Flächenländer insgesamt, 1) -> will not return ARS column
                    - "FDLAND" (Bundesländer, 13)
                    - "FGEMEIN" (Gemeinden, 4795)
                    - "FKREISE" (Kreise und kreisfreie Städte, 411)
                    - "FREGBEZ" (Regierungsbezirke / Statistische Regionen, 41)
                    - "GEMEIN" (Gemeinden, 13565)
                    - "GRSTADT" (Großstadt, 15)
                    - "KREISE" (Kreise und kreisfreie Städte, 489)
                    - "NUTS-2" (NUTS-II Regionen, 38)
                    - "PGEM-2DI" (Gemeinden Pendler, 6857)
                    - "PGEMEIN" (Gemeinden Pendler, 6857)
                    - "REGBEZ" (Regierungsbezirke / Statistische Regionen, 44)

                - Zensusdatenbank (for all tables, see /catalogue/variables):
                    - "GEOBL1" (Bundesländer, 16)
                    - "GEOBL3" (Bundesländer, 16)
                    - "GEOBZ1" (Bezirke (Hamburg und Berlin), 19)
                    - "GEODL1" (Deutschland, 1) -> will not return extra ARS column
                    - "GEODL3" (Deutschland, 1) -> will not return extra ARS column
                    - "GEOGM1" (Gemeinden, 11340)
                    - "GEOGM2" (Gemeinden mit min. 10_000 Einwohnern, 1574)
                    - "GEOGM3" (Gemeinden mit min. 10_000 Einwohnern, 1574)
                    - "GEOGM4" (Gemeinden (Gebietsstand 15.05.2022), 10787)
                    - "GEOGM5" (Gemeinden > 10.000 Einwohner (Stand 15.05.2022), 1578)
                    - "GEOLK1" (Landkreise u. krsfr. Städte (Stand 09.05.11), 412)
                    - "GEOLK3" (Landkreise und kreisfreie Städte, 412)
                    - "GEOLK4" (Landkreise u. krsfr. Städte (Stand 15.05.22), 400)
                    - "GEORB1" (Regierungsbezirke/Statistische Regionen, 36)
                    - "GEORB3" (Regierungsbezirke/Statistische Regionen, 36)
                    - "GEOVB1" (Gemeindeverbände (Gebietsstand 09.05.2011), 1333)
                    - "GEOVB2" (Gemeindeverbände mit mindestens 10 000 Einwohnern, 338)
                    - "GEOVB3" (Gemeindeverbände mit mindestens 10 000 Einwohnern, 157)
                    - "GEOVB4" (Gemeindeverbände (Gebietsstand 15.05.2022), 1207)
                    - "GEOVB5" (Gemeindeverbände > 10.000 Einw. (Stand 15.05.2022), 588)

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
            "area": area,
            "compress": "true" if compress else "false",
            "endyear": endyear,
            "format": "ffcsv",
            "language": language,
            "name": self.name,
            "quality": quality,
            "regionalkey": regionalkey,
            "regionalvariable": regionalvariable,
            "stand": stand,
            "startyear": startyear,
            "timeslices": timeslices,
            "job": "false",
        }

        db_matches = db.identify_db_matches(self.name)
        db_name = db.select_db_by_credentials(db_matches)

        raw_data_bytes = load_data(
            endpoint="data", method="tablefile", params=params, db_name=db_name
        )
        try:
            raw_data_str = raw_data_bytes.decode("utf-8-sig")
        except (AttributeError, UnicodeDecodeError) as e:
            raise ValueError("Failed to decode the raw data as UTF-8") from e

        self.raw_data = raw_data_str

        # sometimes the data contains invalid rows that do not start with the statistics number (always first column)
        # so we have to do this workaround to get a proper data frame later
        raw_data_lines = raw_data_str.splitlines(keepends=True)
        raw_data_header = raw_data_lines[0]
        raw_data_str = raw_data_header + "".join(
            line for line in raw_data_lines[1:] if line[:4].isdigit()
        )
        data_buffer = StringIO(raw_data_str)

        self.data = pd.read_csv(
            data_buffer,
            sep=";",
            na_values=["...", ".", "-", "/", "x"],
            decimal="," if language == "de" else ".",
            dtype={"1_variable_code": str, "1_variable_attribute_code": str},
            parse_dates=[config.LANG_TO_COL_MAPPING[language]["time"]],
            date_format="%Y-%m-%d",
        )

        if prettify:
            self.data = Table.parse_v5_table(self.data, db_name, language)

        metadata = load_data(endpoint="metadata", method="table", params=params)
        metadata = json.loads(metadata)
        if not isinstance(metadata, dict):
            raise TypeError(f"Expected dict for metadata, got {type(metadata).__name__}")

        self.metadata = metadata

    @staticmethod
    def parse_v5_table(data: pd.DataFrame, db_name: str, language: str) -> pd.DataFrame:
        """Transform raw table data into a more readable format.

        This method takes the raw data from GENESIS/Zensus/Regio databases and transforms it
        into a more user-friendly format by:
        1. Handling quality indicators if present
        2. Pivoting the data to have value columns instead of rows
        3. Organizing time, regional codes, and attributes into separate columns
        4. Combining everything into a clean, readable DataFrame

        Args:
            data: Raw DataFrame from the database
            db_name: Database name ('genesis', 'zensus', or 'regio')
            language: Language code ('de' or 'en')

        Returns:
            A restructured DataFrame with a more user-friendly format
        """
        # Get column mappings based on language
        column_mapping = config.LANG_TO_COL_MAPPING[language]

        # Get regional code label (ARS or AGS) based on database and language
        regional_code_label = config.ARS_OR_AGS_MAPPING[db_name][language]

        # Extract column names from mapping
        time_col = column_mapping["time"]
        time_label_col = column_mapping["time_label"]
        value_col = column_mapping["value"]
        value_q_col = column_mapping["value_q"]
        value_unit_col = column_mapping["value_unit"]
        value_variable_label_col = column_mapping["value_variable_label"]
        variable_attribute_label_col = column_mapping["variable_attribute_label"]
        variable_label_col = column_mapping["variable_label"]

        # Check if quality indicators are present
        has_quality_indicators = value_q_col in data.columns

        # Prepare data for pivoting
        data = Table._prepare_data_for_pivot(
            data,
            value_variable_label_col,
            value_unit_col,
            value_col,
            value_q_col,
            has_quality_indicators,
        )

        # Create pivot table and get value columns
        pivot_table, value_columns = Table._create_pivot_table(
            data, value_variable_label_col, value_col, has_quality_indicators
        )

        # Extract time information
        time_df = Table._extract_time_info(data, pivot_table, time_label_col, time_col)

        # Extract regional code information - checks all variable columns for AGS codes
        regional_code_df, is_single_region, regional_code_prefix = Table._extract_regional_codes(
            pivot_table, regional_code_label
        )

        # Extract attribute information
        attributes_df = Table._extract_attributes(
            pivot_table,
            variable_attribute_label_col,
            variable_label_col,
            regional_code_prefix,
        )

        # Prepare components for concatenation
        components = [time_df, attributes_df, pivot_table[value_columns]]

        # Insert regional code DataFrame if needed (when it's a regional code and has multiple regions)
        if regional_code_prefix and not is_single_region:
            # Insert regional columns after time column
            components.insert(1, regional_code_df)

        # Combine all components into final DataFrame
        pretty_data = pd.concat(components, axis=1)

        return pretty_data

    @staticmethod
    def _prepare_data_for_pivot(
        data: pd.DataFrame,
        value_variable_label_col: str,
        value_unit_col: str,
        value_col: str,
        value_q_col: str,
        has_quality_indicators: bool,
    ) -> pd.DataFrame:
        """Prepare data for pivoting by adding units to column names and handling quality indicators."""
        # Add the unit to the column names for the value columns
        data[value_variable_label_col] = data[value_variable_label_col].str.cat(
            data[value_unit_col].astype(str).fillna("Unknown_Unit"), sep="__"
        )

        if has_quality_indicators:
            # With quality = 'on' we have an additional column value_q
            # To still use pivot table we have to combine value and value_q
            # so we can later split them again
            data[value_col] = [[v, q] for v, q in zip(data[value_col], data[value_q_col])]
            data = data.drop(columns=[value_q_col])

        return data

    @staticmethod
    def _create_pivot_table(
        data: pd.DataFrame,
        value_variable_label_col: str,
        value_col: str,
        has_quality_indicators: bool,
    ) -> tuple[pd.DataFrame, list[str]]:
        """Create a pivot table from the prepared data.

        Returns:
            A tuple containing:
            - The pivot table with reset index
            - A list of value column names
        """
        # Create pivot table with all non-value columns as index
        pivot_table = data.pivot(
            index=[col for col in data.columns if col not in data.filter(regex=r"^value").columns],
            columns=value_variable_label_col,
            values=value_col,
        )

        # Store the value column names before resetting the index
        value_columns = pivot_table.columns.to_list()

        # Handle quality indicators if present
        if has_quality_indicators:
            for col in pivot_table.columns:
                # Insert quality column right after the value column
                pivot_table.insert(
                    pivot_table.columns.to_list().index(col) + 1,
                    col + "__q",
                    pivot_table[col].apply(lambda x: x[1]),
                )
                # Extract the actual value from the combined [value, quality] list
                pivot_table[col] = pivot_table[col].apply(lambda x: x[0])

            # Update value columns list to include both value and quality columns
            # The quality columns have already been added to the pivot table
            value_columns = pivot_table.columns.to_list()

        # Reset index to convert index columns back to regular columns
        pivot_table.reset_index(inplace=True)
        pivot_table.columns.name = None

        # Return the pivot table and the value column names
        return pivot_table, value_columns

    @staticmethod
    def _extract_time_info(
        data: pd.DataFrame,
        pivot_table: pd.DataFrame,
        time_label_col: str,
        time_col: str,
    ) -> pd.DataFrame:
        """Extract time information into a separate DataFrame."""
        time_label = data[time_label_col].iloc[0]
        return pd.DataFrame({time_label: pivot_table[time_col]})

    @staticmethod
    def _extract_regional_codes(
        pivot_table: pd.DataFrame, regional_code_label: str
    ) -> tuple[pd.DataFrame, bool, str]:
        """Extract regional code information into a separate DataFrame.

        Checks all variable code columns to find a column containing a known AGS code.

        Returns:
            Tuple containing:
            - DataFrame with regional code columns
            - Boolean indicating if there's only a single region
            - String with the column prefix of the regional code column (e.g., "1" for "1_variable_code")
                or empty string if no regional code was found
        """
        # Get all variable code columns
        var_code_cols = pivot_table.filter(regex=r"\d+_variable_code")

        if var_code_cols.empty or len(pivot_table) == 0:
            return pd.DataFrame(), False, ""

        # Check each variable code column for known AGS codes
        for col_name in var_code_cols.columns:
            # Get all non-NaN values in the column
            var_codes = pivot_table[col_name].dropna().unique()

            # Check if any of the codes in the column is a known AGS code
            if any(code in config.AGS_CODES for code in var_codes):
                # Found a regional code, get the corresponding attribute code and label columns
                # The column index is extracted from the column name (e.g., "1_variable_code" -> "1")
                col_prefix = col_name.split("_")[0]
                attr_code_col = f"{col_prefix}_variable_attribute_code"
                attr_label_col = f"{col_prefix}_variable_attribute_label"

                # Create the regional DataFrame
                regional_df = pd.DataFrame(
                    {
                        regional_code_label + "__Code": pivot_table[attr_code_col],
                        regional_code_label: pivot_table[attr_label_col],
                    }
                )
                is_single_region = regional_df[regional_code_label].unique().size == 1

                # Return the regional code information, single region flag, and column prefix
                return regional_df, is_single_region, col_prefix

        # No regional code found in any column
        return pd.DataFrame(), False, ""

    @staticmethod
    def _extract_attributes(
        pivot_table: pd.DataFrame,
        variable_attribute_label_col: str,
        variable_label_col: str,
        regional_code_prefix: str = "",
    ) -> pd.DataFrame:
        """Extract attribute information into a separate DataFrame.

        Args:
            pivot_table: The pivot table containing the data
            variable_attribute_label_col: The column name pattern for attribute labels
            variable_label_col: The column name pattern for variable labels
            regional_code_prefix: The column prefix of the regional code column (e.g., "1" for "1_variable_code")
                or empty string if no regional code was found

        Returns:
            DataFrame containing attribute columns
        """
        # Get all attribute columns
        all_attribute_cols = pivot_table.filter(regex=r"\d+_" + variable_attribute_label_col)

        # If a regional code was found, exclude that specific column
        if regional_code_prefix:
            regional_col = f"{regional_code_prefix}_{variable_attribute_label_col}"
            attributes = all_attribute_cols.loc[:, all_attribute_cols.columns != regional_col]
        else:
            attributes = all_attribute_cols

        # Get the variable labels for each attribute column
        var_label_cols = pivot_table.filter(regex=r"\d+_" + variable_label_col)

        # Create a mapping from column prefix to variable label
        label_mapping = {}

        # Find the first row with valid labels
        for _, row in var_label_cols.iterrows():
            if not row.isna().any():
                for col_name, label in zip(var_label_cols.columns, row):
                    prefix = col_name.split("_")[0]
                    # Skip the regional code column if one was found
                    if not regional_code_prefix or prefix != regional_code_prefix:
                        label_mapping[prefix] = label
                break

        # Map each attribute column to its corresponding variable label
        valid_labels = []
        for col_name in attributes.columns:
            prefix = col_name.split("_")[0]
            if prefix in label_mapping:
                valid_labels.append(label_mapping[prefix])

        # Set column names if valid labels were found
        if valid_labels and len(valid_labels) == len(attributes.columns):
            attributes.columns = valid_labels

        return attributes
