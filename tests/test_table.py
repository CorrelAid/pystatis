import logging
import time

import pandas as pd
import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime

import pystatis

pystatis.clear_cache()


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, language",
    [
        # German tables
        ("12211-0001", (225, 21), "de"),
        ("13111-0005", (384, 17), "de"),
        ("23111-0001", (264, 13), "de"),
        ("23311-0010", (4352, 25), "de"),
        ("32161-0003", (70, 17), "de"),
        ("32421-0012", (2240, 21), "de"),
        ("46181-0001", (16, 21), "de"),
        ("51000-0010", (1572, 21), "de"),
        ("61111-0021", (960, 17), "de"),
        ("63121-0001", (210, 21), "de"),
        ("71311-0001", (600, 25), "de"),
        ("91111-0001", (4719, 17), "de"),
        ("11111-02-01-4", (550, 13), "de"),
        ("13111-01-03-4", (3300, 21), "de"),
        ("21311-01-01-4-B", (44010, 25), "de"),
        ("32121-01-02-4", (3850, 17), "de"),
        ("41312-01-01-4", (6050, 17), "de"),
        # ("52411-02-01-4", (538, 15), "de"), # currently broken, returns 500
        ("61511-01-03-4", (4400, 17), "de"),
        ("73111-01-01-4", (1650, 13), "de"),
        ("86121-Z-01", (8208, 17), "de"),
        ("AI-N-01-2-5", (27128, 13), "de"),
        ("1000A-0000", (10787, 13), "de"),
        ("2000S-2003", (72, 21), "de"),
        ("3000G-1008", (20, 17), "de"),
        ("4000W-2041", (180, 21), "de"),
        # English tables
        ("12211-0001", (225, 21), "en"),
        ("13111-0005", (384, 17), "en"),
        ("23111-0001", (264, 13), "en"),
        ("23311-0010", (4352, 25), "en"),
        ("32161-0003", (70, 17), "en"),
        ("32421-0012", (2240, 21), "en"),
        ("46181-0001", (16, 21), "en"),
        ("51000-0010", (1572, 21), "en"),
        ("61111-0021", (960, 17), "en"),
        ("63121-0001", (210, 21), "en"),
        ("71311-0001", (600, 25), "en"),
        ("91111-0001", (4719, 17), "en"),
        ("1000A-0000", (10787, 13), "en"),
        ("2000S-2003", (72, 21), "en"),
        ("3000G-1008", (20, 17), "en"),
        ("4000W-2041", (180, 21), "en"),
    ],
)
def test_get_data(mocker, table_name: str, expected_shape: tuple[int, int], language: str):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False, language=language, compress=False)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty
    assert isinstance(table.raw_data, str)
    assert table.raw_data != ""

    assert table.data.shape == expected_shape


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape",
    [
        ("52111-0001", (68, 22)),
        ("12211-Z-11", (2200, 18)),
        ("1000A-2022", (1360, 22)),
    ],
)
def test_get_data_with_quality_on_and_prettify_false(
    mocker, table_name: str, expected_shape: tuple[int, int]
):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False, quality="on", compress=False)

    assert table.data.shape == expected_shape

    # check that at least one raw column ends with "_q" for zensus + quality
    assert any(column.endswith("value_q") for column in table.data.columns)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape",
    [
        ("1000A-2022", (1003, 6)),
    ],
)
def test_get_data_with_compress_on(mocker, table_name: str, expected_shape: tuple):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data()

    assert table.data.shape == expected_shape
    assert table.data["Personen__Anzahl"].isna().sum() == 0


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, expected_columns",
    [
        (
            "52111-0001",
            (68, 5),
            (
                "Jahr",
                "Beschäftigtengrößenklassen",
                "WZ2008 (Abschnitte): URS",
                "Unternehmen (EU)__Anzahl",
                "Unternehmen (EU)__Anzahl__q",
            ),
        ),
        (
            "12211-Z-11",
            (2200, 6),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Art der Lebensform",
                "Lebensformen__1000",
                "Lebensformen__1000__q",
            ),
        ),
        (
            "1000A-2022",
            (1360, 7),
            (
                "Stichtag",
                "Amtlicher Regionalschlüssel (ARS)__Code",
                "Amtlicher Regionalschlüssel (ARS)",
                "Alter (10er-Jahresgruppen)",
                "Einwanderungsgeschichte (ausführlich)",
                "Personen__Anzahl",
                "Personen__Anzahl__q",
            ),
        ),
    ],
)
def test_get_data_with_quality_on_and_prettify_true(
    mocker,
    table_name: str,
    expected_shape: tuple[int, int],
    expected_columns: tuple[str],
):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, quality="on", compress=False)

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, expected_columns, language",
    [
        (
            "12211-0001",
            (45, 8),
            (
                "Jahr",
                "Geschlecht",
                "Altersgruppen (u15-75m)",
                "Bevölkerung in Hauptwohnsitzhaushalten__1000",
                "Erwerbslose aus Hauptwohnsitzhaushalten__1000",
                "Erwerbspersonen aus Hauptwohnsitzhaushalten__1000",
                "Erwerbstätige aus Hauptwohnsitzhaushalten__1000",
                "Nichterwerbspersonen aus Hauptwohnsitzhaushalten__1000",
            ),
            "de",
        ),
        (
            "13111-0005",
            (384, 5),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Geschlecht",
                "Sozialvers.pflichtig Beschäftigte am Arbeitsort__Anzahl",
            ),
            "de",
        ),
        (
            "23111-0001",
            (33, 9),
            (
                "Jahr",
                "Berechnungs-/Belegungstage__1000",
                "Betten je 100.000 Einwohner__Anzahl",
                "Betten__Anzahl",
                "Durchschnittliche Bettenauslastung__Prozent",
                "Durchschnittliche Verweildauer__Tage",
                "Krankenhäuser__Anzahl",
                "Patienten je 100.000 Einwohner__Anzahl",
                "Patienten__Anzahl",
            ),
            "de",
        ),
        (
            "23311-0010",
            (4352, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Quartale",
                "Herkunfts-Bundesland oder Ausland",
                "Familienstand",
                "Schwangerschaftsabbrüche__Anzahl",
            ),
            "de",
        ),
        (
            "32161-0003",
            (14, 7),
            (
                "Jahr",
                "WZ2008 (2-Steller): Abfallerzeugung",
                "Beschäftigte__1000",
                "Betriebe__Anzahl",
                "Erfassungsgrad der Beschäftigten__Prozent",
                "Erfassungsgrad der Betriebe__Prozent",
                "Erzeugte Abfallmenge__1000 t",
            ),
            "de",
        ),
        (
            "32421-0012",
            (1120, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Stoffgruppen",
                "Einsatzbereiche",
                "Verwendung klimawirksamer Stoffe (CO2-Äquivalente)__1000 t",
                "Verwendung klimawirksamer Stoffe__t",
            ),
            "de",
        ),
        (
            "46181-0001",
            (8, 5),
            (
                "Jahr",
                "Verkehrsart",
                "Hauptverkehrsverbindung",
                "Beförderte Personen__Anzahl",
                "Beförderungsleistung__Person-km",
            ),
            "de",
        ),
        (
            "51000-0010",
            (262, 9),
            (
                "Jahr",
                "Länderverzeichnis für die Außenhandelsstatistik",
                "Warenverzeichnis Außenhandelsstatistik (4-Steller)",
                "Ausfuhr: Gewicht__t",
                "Ausfuhr: Wert (US-Dollar)__Tsd. US $",
                "Ausfuhr: Wert__Tsd. EUR",
                "Einfuhr: Gewicht__t",
                "Einfuhr: Wert (US-Dollar)__Tsd. US $",
                "Einfuhr: Wert__Tsd. EUR",
            ),
            "de",
        ),
        (
            "61111-0021",
            (960, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Monate",
                "Index der Nettokaltmieten__2020=100",
            ),
            "de",
        ),
        (
            "63121-0001",
            (180, 6),
            (
                "Jahr",
                "Haushaltsgröße",
                "Einnahme- und Ausgabearten",
                "Durchschnittsbetrag je Haushalt und Monat__EUR",
                "Erfasste Haushalte__Anzahl",
                "Hochgerechnete Haushalte__1000",
            ),
            "de",
        ),
        (
            "71311-0001",
            (600, 5),
            (
                "Stichtag zum Quartalsende",
                "Ebenen des öffentlichen Gesamthaushalts",
                "Haushalte",
                "Schuldenarten",
                "Schulden beim nicht-öffentlichen Bereich__Mill. EUR",
            ),
            "de",
        ),
        (
            "91111-0001",
            (4719, 3),
            (
                "Jahr",
                "Indikatoren: Nachhaltige Entwicklung",
                "Indikatoren__jew. ME",
            ),
            "de",
        ),
        (
            "11111-02-01-4",
            (550, 4),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Zahl der Gemeinden__Anzahl",
            ),
            "de",
        ),
        (
            "21311-01-01-4-B",
            (44010, 7),
            (
                "Semester",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Geschlecht",
                "Nationalität (inkl. insgesamt)",
                "Fächergruppe (mit Insgesamt)",
                "Studierende (im Kreisgebiet)__Anzahl",
            ),
            "de",
        ),
        (
            "32121-01-02-4",
            (3850, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Abfallarten von Haushaltsabfällen",
                "Aufkommen an Haushaltsabfällen (oh.Elektroaltger.)__t",
            ),
            "de",
        ),
        (
            "41312-01-01-4",
            (6050, 5),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Tierarten",
                "Tiere__Anzahl",
            ),
            "de",
        ),
        # # (
        # #     "52411-02-01-4",
        # #     (538, 6),
        # #     (
        # #         "Jahr",
        # #         "Amtlicher Gemeindeschlüssel (AGS)__Code",
        # #         "Amtlicher Gemeindeschlüssel (AGS)",
        # #         "Insolvenzverfahren (Unternehmen)__MeasureUnitNotFound!",
        # #         "Arbeitnehmer__Anzahl",
        # #         "voraussichtliche Forderungen (Unternehmen)__Tsd._EUR",
        # #     ),
        # #     "de",
        # # ),
        (
            "61511-01-03-4",
            (1100, 8),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Baulandverkäufe",
                "Durchschnittlicher Kaufwert je qm__EUR",
                "Kaufsumme__Tsd. EUR",
                "Veräußerte Baulandfläche__1000 qm",
                "Veräußerungsfälle von Bauland__Anzahl",
            ),
            "de",
        ),
        (
            "73111-01-01-4",
            (550, 6),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Gesamtbetrag der Einkünfte__Tsd. EUR",
                "Lohn- und Einkommensteuer__Tsd. EUR",
                "Lohn- und Einkommensteuerpflichtige__Anzahl",
            ),
            "de",
        ),
        (
            "86121-Z-01",
            (2736, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Haushaltsabfälle",
                "Haushaltsabfälle, Anteil an Deutschland__Prozent",
                "Haushaltsabfälle, Index (2010=100)__2010=100",
                "Haushaltsabfälle__1000 t",
            ),
            "de",
        ),
        (
            "AI-N-01-2-5",
            (13564, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)__Code",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Anteil Siedlungs- und Verkehrsfläche an Gesamtfläche__Prozent",
                "Veränderung der Siedlungs- und Verkehrsfläche__Prozent",
            ),
            "de",
        ),
        (
            "1000A-0000",
            (10787, 4),
            (
                "Stichtag",
                "Amtlicher Regionalschlüssel (ARS)__Code",
                "Amtlicher Regionalschlüssel (ARS)",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "2000S-2003",
            (72, 4),
            (
                "Stichtag",
                "Einwanderungsgeschichte (ausführlich)",
                "Erwerbsstatus",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "3000G-1008",
            (10, 4),
            (
                "Stichtag",
                "Energieträger der Heizung",
                "Gebäude mit Wohnraum__%",
                "Gebäude mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "4000W-2030",
            (286, 4),
            (
                "Stichtag",
                "Miete der Wohnung (100 €-Schritte)",
                "Gebäudetyp (Größe)",
                "Vermietete Wohnungen in Gebäuden mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "81000-0001",
            (40, 9),
            (
                "Jahr",
                "Preisbasis (jeweilige Preise / preisbereinigt)",
                "Bruttoinlandsprodukt (Veränderung in %)__Prozent",
                "Bruttoinlandsprodukt je Einwohner__jew. ME",
                "Bruttoinlandsprodukt__jew. ME",
                "Bruttowertschöpfung__jew. ME",
                "Gütersteuern abzügl. Gütersubventionen__jew. ME",
                "Gütersteuern__jew. ME",
                "Gütersubventionen__jew. ME",
            ),
            "de",
        ),
        (
            "12211-0001",
            (45, 8),
            (
                "Year",
                "Sex",
                "Age groups (under 15 - 75 years and over)",
                "Economically active population from prim.resid.hh.__1000",
                "Economically inactive population fr.prim.resid.hh.__1000",
                "Persons in employment from primary residence hh.__1000",
                "Population in primary residence households__1000",
                "Unemployed persons from primary residence hh.__1000",
            ),
            "en",
        ),
        (
            "13111-0005",
            (384, 5),
            (
                "Reference date",
                "Official municipality key (AGS)__Code",
                "Official municipality key (AGS)",
                "Sex",
                "Employees subj. to social insur. at place of work__number",
            ),
            "en",
        ),
        (
            "23111-0001",
            (33, 9),
            (
                "Year",
                "Average length of stay__days",
                "Average occupancy of hospital beds__percent",
                "Beds per 100 000 inhabitants__number",
                "Beds__number",
                "Hospitals__number",
                "Occupancy / billing days__1000",
                "Patients per 100 000 inhabitants__number",
                "Patients__number",
            ),
            "en",
        ),
        (
            "23311-0010",
            (4352, 7),
            (
                "Year",
                "Official municipality key (AGS)__Code",
                "Official municipality key (AGS)",
                "Quarters",
                "Land of origin or origin from abroad",
                "Marital status",
                "Terminations of pregnancy__number",
            ),
            "en",
        ),
        (
            "32161-0003",
            (14, 7),
            (
                "Year",
                "WZ2008 (2-digit codes): Waste production",
                "Coverage of local units__percent",
                "Coverage of persons employed__percent",
                "Local units__number",
                "Persons employed__1000",
                "Quantity of waste produced__1000 t",
            ),
            "en",
        ),
        (
            "32421-0012",
            (1120, 7),
            (
                "Year",
                "Official municipality key (AGS)__Code",
                "Official municipality key (AGS)",
                "Groups of substances",
                "Application areas",
                "Use of climate-affecting substances (CO2-equiv.)__1000 t",
                "Use of climate-affecting substances__t",
            ),
            "en",
        ),
        (
            "46181-0001",
            (8, 5),
            (
                "Year",
                "Type of transport",
                "Main traffic relation",
                "Passengers carried__number",
                "Transport performance__pass-km",
            ),
            "en",
        ),
        (
            "51000-0010",
            (262, 9),
            (
                "Year",
                "Country Nomenclature for External Trade Statistics",
                "Commodity Class. Foreign Trade Stat.(4-digit cod.)",
                "Exports: Net mass__t",
                "Exports: Value (US-Dollar)__US-$ 1000",
                "Exports: Value__EUR 1000",
                "Imports: Net mass__t",
                "Imports: Value (US-Dollar)__US-$ 1000",
                "Imports: Value__EUR 1000",
            ),
            "en",
        ),
        (
            "61111-0021",
            (960, 5),
            (
                "Year",
                "Official municipality key (AGS)__Code",
                "Official municipality key (AGS)",
                "Months",
                "Index of net rents exclusive of heating expenses__2020=100",
            ),
            "en",
        ),
        (
            "63121-0001",
            (180, 6),
            (
                "Year",
                "Household size",
                "Types of income and expenditure",
                "Average amount per household and month__EUR",
                "Households covered__number",
                "Households extrapolated__1000",
            ),
            "en",
        ),
        (
            "71311-0001",
            (600, 5),
            (
                "Reference date end-of-quarter",
                "Levels of the overall public budget",
                "Budgets",
                "Types of debts",
                "Debts owed to the non-public sector__EUR mn",
            ),
            "en",
        ),
        (
            "91111-0001",
            (4719, 3),
            (
                "Year",
                "Indicators: Sustainable development",
                "Indicators__unit app.",
            ),
            "en",
        ),
        (  # currently broken in English, API returns rows with missing columns
            "1000A-0000",
            (10787, 4),
            (
                "Reference date",
                "Official regional key (ARS)__Code",
                "Official regional key (ARS)",
                "Persons__number",
            ),
            "en",
        ),
        (
            "2000S-2003",
            (72, 4),
            (
                "Reference date",
                "Immigration history (in detail)",
                "Activity status",
                "Persons__number",
            ),
            "en",
        ),
        (
            "3000G-1008",
            (10, 4),
            (
                "Reference date",
                "Energy source used for heating",
                "Buildings with residential space__%",
                "Buildings with residential space__number",
            ),
            "en",
        ),
        (
            "4000W-2041",
            (90, 5),
            (
                "Reference date",
                "Duration of dwelling vacancy",
                "Floor area of the dwelling (10m² increments)",
                "Vacant dwellings in buildings with residential space__%",
                "Vacant dwellings in buildings with residential space__number",
            ),
            "en",
        ),
    ],
)
def test_prettify(
    mocker,
    table_name: str,
    expected_shape: tuple[int, int],
    expected_columns: tuple[str],
    language: str,
):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, language=language, compress=False)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, time_col, language",
    [
        ("12411-01-01-4", "Stichtag", "de"),
        ("12411-01-01-4", "Stichtag", "en"),
        ("13111-0005", "Stichtag", "de"),
        ("13111-0005", "Reference date", "en"),
        ("71311-0001", "Stichtag zum Quartalsende", "de"),
        ("71311-0001", "Reference date end-of-quarter", "en"),
        ("1000A-0000", "Stichtag", "de"),
        ("1000A-0000", "Reference date", "en"),
        ("2000S-2003", "Stichtag", "de"),
        ("2000S-2003", "Reference date", "en"),
    ],
)
def test_dtype_time_column(mocker, table_name: str, time_col: str, language: str):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, language=language, compress=False)

    assert is_datetime(table.data[time_col].values)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name",
    [
        ("12531-0043"),
    ],
)
def test_get_data_with_job(mocker, caplog, table_name):
    mocker.patch.object(pystatis.db, "check_credentials_are_set", return_value=True)
    mocker.patch.object(time, "sleep", return_value=0)
    caplog.set_level(logging.DEBUG)

    table = pystatis.Table(name=table_name)
    table.get_data()

    assert "Die Tabelle ist zu groß, um direkt abgerufen zu werden" in caplog.text
    assert "Verarbeitung im Hintergrund erfolgreich gestartet" in caplog.text
    assert "Verarbeitung im Hintergrund abgeschlossen" in caplog.text

    assert not table.data.empty
