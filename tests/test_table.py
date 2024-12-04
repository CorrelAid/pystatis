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
        ("32421-0012", (1120, 21), "de"),
        ("46181-0001", (16, 21), "de"),
        ("51000-0010", (1572, 21), "de"),
        ("61111-0021", (960, 17), "de"),
        ("63121-0001", (210, 21), "de"),
        ("71311-0001", (600, 25), "de"),
        ("91111-0001", (4719, 17), "de"),
        ("11111-02-01-4", (538, 10), "de"),
        ("13111-01-03-4", (3228, 18), "de"),
        ("21311-01-01-4-B", (44010, 22), "de"),
        ("32121-01-02-4", (3766, 14), "de"),
        ("41312-01-01-4", (5918, 14), "de"),
        ("52411-02-01-4", (538, 12), "de"),
        ("61511-01-03-4", (1076, 17), "de"),
        ("73111-01-01-4", (538, 12), "de"),
        ("86121-Z-01", (2736, 16), "de"),
        ("AI-N-01-2-5", (13922, 11), "de"),
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
        ("32421-0012", (1120, 21), "en"),
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
def test_get_data(
    mocker, table_name: str, expected_shape: tuple[int, int], language: str
):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False, language=language)

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
        ("12211-Z-11", (2152, 14)),
        ("1000A-2022", (1360, 22)),
    ],
)
def test_get_data_with_quality_on_and_prettify_false(
    mocker, table_name: str, expected_shape: tuple[int, int]
):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False, quality="on")

    assert table.data.shape == expected_shape

    if table_name in ["1000A-2022", "52111-0001"]:
        # check that at least one raw column ends with "_q" for zensus + quality
        assert any(column.endswith("value_q") for column in table.data.columns)
    elif table_name == "12211-Z-11":
        # check that at least no raw column ends with "__q" for regio + quality
        # (API call with quality="on" does not support quality for regio tables)
        assert not any(column.endswith("__q") for column in table.data.columns)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, expected_columns",
    [
        (
            "52111-0001",
            (68, 6),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Beschäftigtengrößenklassen",
                "WZ2008 (Abschnitte): URS",
                "Unternehmen (EU)__Anzahl",
                "Unternehmen (EU)__Anzahl__q",
            ),
        ),
        (
            "12211-Z-11",
            (2152, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Art der Lebensform",
                "Lebensformen am Hauptwohnort__1000",
            ),
        ),
        (
            "1000A-2022",
            (1360, 7),
            (
                "Stichtag",
                "Amtlicher Regionalschlüssel (ARS)",
                "Bundesländer",
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
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, quality="on")

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, expected_columns, language",
    [
        (
            "12211-0001",
            (45, 9),
            (
                "Jahr",
                "Deutschland insgesamt",
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
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Geschlecht",
                "Sozialvers.pflichtig Beschäftigte am Arbeitsort__Anzahl",
            ),
            "de",
        ),
        (
            "23111-0001",
            (33, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
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
                "Quartale",
                "Herkunfts-Bundesland oder Ausland",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Familienstand",
                "Schwangerschaftsabbrüche__Anzahl",
            ),
            "de",
        ),
        (
            "32161-0003",
            (14, 8),
            (
                "Jahr",
                "Deutschland insgesamt",
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
            (560, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Stoffgruppen",
                "Einsatzbereiche",
                "Verwendung klimawirksamer Stoffe (CO2-Äquivalente)__1000 t",
                "Verwendung klimawirksamer Stoffe__t",
            ),
            "de",
        ),
        (
            "46181-0001",
            (8, 6),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Verkehrsart",
                "Hauptverkehrsverbindung",
                "Beförderte Personen__Anzahl",
                "Beförderungsleistung__Person-km",
            ),
            "de",
        ),
        (
            "51000-0010",
            (262, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
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
                "Monate",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Index der Nettokaltmieten__2020=100",
            ),
            "de",
        ),
        (
            "63121-0001",
            (180, 7),
            (
                "Jahr",
                "Deutschland insgesamt",
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
            (600, 6),
            (
                "Stichtag zum Quartalsende",
                "Deutschland insgesamt",
                "Ebenen des öffentlichen Gesamthaushalts",
                "Haushalte",
                "Schuldenarten",
                "Schulden beim nicht-öffentlichen Bereich__Mill. EUR",
            ),
            "de",
        ),
        (
            "91111-0001",
            (4719, 4),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Indikatoren: Nachhaltige Entwicklung",
                "Indikatoren__jew. ME",
            ),
            "de",
        ),
        (
            "11111-02-01-4",
            (538, 4),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Zahl der Gemeinden__Anzahl",
            ),
            "de",
        ),
        (
            "21311-01-01-4-B",
            (44010, 7),
            (
                "Semester",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Geschlecht",
                "Nationalität (inkl. insgesamt)",
                "Fächergruppe (mit Insgesamt)",
                "Studierende (im Kreisgebiet)__Anzahl",
            ),
            "de",
        ),
        (
            "32121-01-02-4",
            (3766, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Abfallarten von Haushaltsabfällen",
                "Aufkommen an Haushaltsabfaellen (o.E-altgeraete)__t",
            ),
            "de",
        ),
        (
            "41312-01-01-4",
            (5918, 5),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Tierarten",
                "Tiere__Anzahl",
            ),
            "de",
        ),
        (
            "52411-02-01-4",
            (538, 6),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Insolvenzverfahren (Unternehmen)__MeasureUnitNotFound!",
                "Arbeitnehmer__Anzahl",
                "voraussichtliche Forderungen (Unternehmen)__Tsd._EUR",
            ),
            "de",
        ),
        (
            "61511-01-03-4",
            (1076, 8),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Baulandverkäufe",
                "Veraeusserungsfaelle von Bauland__Anzahl",
                "Veraeusserte Baulandflaeche__1000_qm",
                "Kaufsumme__Tsd._EUR",
                "Durchschnittlicher Kaufwert je qm__EUR",
            ),
            "de",
        ),
        (
            "73111-01-01-4",
            (538, 6),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Lohn- und Einkommensteuerpflichtige__Anzahl",
                "Gesamtbetrag der Einkuenfte__Tsd._EUR",
                "Lohn- und Einkommensteuer__Tsd._EUR",
            ),
            "de",
        ),
        (
            "86121-Z-01",
            (2736, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Haushaltsabfälle",
                "Haushaltsabfaelle__1000_t",
                "Haushaltsabfaelle, Index (2010=100)__2010=100",
                "Haushaltsabfaelle, Anteil an Deutschland__Prozent",
            ),
            "de",
        ),
        (
            "AI-N-01-2-5",
            (13922, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Gemeinden",
                "Anteil Siedlungs- und Verkehrsflaeche an Gesamtflaeche__Prozent",
                "Veraenderung der Siedlungs- und Verkehrsflaeche__Prozent",
            ),
            "de",
        ),
        (
            "1000A-0000",
            (10787, 4),
            (
                "Stichtag",
                "Amtlicher Regionalschlüssel (ARS)",
                "Gemeinden (Gebietsstand 15.05.2022)",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "2000S-2003",
            (72, 5),
            (
                "Stichtag",
                "Deutschland",
                "Einwanderungsgeschichte (ausführlich)",
                "Erwerbsstatus",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "3000G-1008",
            (10, 5),
            (
                "Stichtag",
                "Deutschland",
                "Energieträger der Heizung",
                "Gebäude mit Wohnraum__%",
                "Gebäude mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "4000W-2030",
            (286, 5),
            (
                "Stichtag",
                "Deutschland",
                "Miete der Wohnung (100 €-Schritte)",
                "Gebäudetyp (Größe)",
                "Vermietete Wohnungen in Gebäuden mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "81000-0001",
            (40, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
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
            (45, 9),
            (
                "Year",
                "Germany",
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
                "Official municipality key (AGS)",
                "Länder",
                "Sex",
                "Employees subj. to social insur. at place of work__number",
            ),
            "en",
        ),
        (
            "23111-0001",
            (33, 10),
            (
                "Year",
                "Germany",
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
                "Quarters",
                "Land of origin or origin from abroad",
                "Official municipality key (AGS)",
                "Länder",
                "Marital status",
                "Terminations of pregnancy__number",
            ),
            "en",
        ),
        (
            "32161-0003",
            (14, 8),
            (
                "Year",
                "Germany",
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
            (560, 7),
            (
                "Year",
                "Official municipality key (AGS)",
                "Länder",
                "Groups of substances",
                "Application areas",
                "Use of climate-affecting substances (CO2-equiv.)__1000 t",
                "Use of climate-affecting substances__t",
            ),
            "en",
        ),
        (
            "46181-0001",
            (8, 6),
            (
                "Year",
                "Germany",
                "Type of transport",
                "Main traffic relation",
                "Passengers carried__number",
                "Transport performance__pass-km",
            ),
            "en",
        ),
        (
            "51000-0010",
            (262, 10),
            (
                "Year",
                "Germany",
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
                "Months",
                "Official municipality key (AGS)",
                "Länder",
                "Index of net rents exclusive of heating expenses__2020=100",
            ),
            "en",
        ),
        (
            "63121-0001",
            (180, 7),
            (
                "Year",
                "Germany",
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
            (600, 6),
            (
                "Reference date end-of-quarter",
                "Germany",
                "Levels of the overall public budget",
                "Budgets",
                "Types of debts",
                "Debts owed to the non-public sector__EUR mn",
            ),
            "en",
        ),
        (
            "91111-0001",
            (4719, 4),
            (
                "Year",
                "Germany",
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
                "Official regional key (ARS)",
                "Municipalities (territory on 15 May 2022, LAU-2)",
                "Persons__number",
            ),
            "en",
        ),
        (
            "2000S-2003",
            (72, 5),
            (
                "Reference date",
                "Germany",
                "Immigration history (in detail)",
                "Activity status",
                "Persons__number",
            ),
            "en",
        ),
        (
            "3000G-1008",
            (10, 5),
            (
                "Reference date",
                "Germany",
                "Energy source used for heating",
                "Buildings with residential space__%",
                "Buildings with residential space__number",
            ),
            "en",
        ),
        (
            "4000W-2041",
            (90, 6),
            (
                "Reference date",
                "Germany",
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
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, language=language)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, time_col, language",
    [("12411-01-01-4", "Stichtag", "de"), ("12411-01-01-4", "Stichtag", "en")],
)
def test_dtype_time_column(mocker, table_name: str, time_col: str, language: str):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, language=language)

    assert is_datetime(table.data[time_col].values)
