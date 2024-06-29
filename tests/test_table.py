import pandas as pd
import pytest

import pystatis

pystatis.clear_cache()


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, language",
    [
        ("12211-0001", (45, 22), "de"),
        ("13111-0005", (384, 14), "de"),
        ("23111-0001", (32, 17), "de"),
        ("23311-0010", (4352, 22), "de"),
        ("32161-0003", (14, 18), "de"),
        ("32421-0012", (560, 19), "de"),
        ("46181-0001", (8, 19), "de"),
        ("51000-0010", (262, 23), "de"),
        ("61111-0021", (960, 14), "de"),
        ("63121-0001", (180, 20), "de"),
        ("71311-0001", (600, 22), "de"),
        ("91111-0001", (6600, 14), "de"),
        ("11111-02-01-4", (538, 10), "de"),
        ("13111-01-03-4", (3228, 18), "de"),
        ("21311-01-01-4-B", (44010, 22), "de"),
        ("32121-01-02-4", (3766, 14), "de"),
        ("41312-01-01-4", (5918, 14), "de"),
        ("52411-02-01-4", (538, 12), "de"),
        ("61511-01-03-4", (1076, 17), "de"),
        ("73111-01-01-4", (538, 12), "de"),
        ("86000U-Z-01", (2052, 16), "de"),
        ("AI-N-01-2-5", (13922, 11), "de"),
        ("1000A-0001", (34017, 13), "de"),
        ("2000S-2003", (110, 21), "de"),
        ("3000G-1008", (14, 17), "de"),
        ("4000W-5003", (4950, 33), "de"),
        ("12211-0001", (45, 22), "en"),
        ("13111-0005", (384, 14), "en"),
        ("23111-0001", (32, 17), "en"),
        ("23311-0010", (4352, 22), "en"),
        ("32161-0003", (14, 18), "en"),
        ("32421-0012", (560, 19), "en"),
        ("46181-0001", (8, 19), "en"),
        ("51000-0010", (262, 23), "en"),
        ("61111-0021", (960, 14), "en"),
        ("63121-0001", (180, 20), "en"),
        ("71311-0001", (600, 22), "en"),
        ("91111-0001", (6600, 14), "en"),
        ("1000A-0001", (34017, 13), "en"),
        ("2000S-2003", (110, 21), "en"),
        ("3000G-1008", (14, 17), "en"),
        ("4000W-5003", (4950, 33), "en"),
    ],
)
def test_get_data(mocker, table_name: str, expected_shape: tuple[int, int], language: str):
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
        ("52111-0001", (68, 19)),
        ("12211-Z-11", (2152, 14)),
        ("6000F-1007", (10, 18)),
    ],
)
def test_get_data_with_quality_on_and_prettify_false(mocker, table_name: str, expected_shape: tuple[int, int]):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False, quality="on")

    assert table.data.shape == expected_shape

    if table_name == "6000F-1007":
        # check that at least one raw column ends with "_q" for zensus + quality
        assert any(column.endswith("_q") for column in table.data.columns)
    elif table_name == "12211-Z-11":
        # check that at least no raw column ends with "__q" for regio + quality
        # (API call with quality="on" does not support quality for regio tables)
        assert not any(column.endswith("__q") for column in table.data.columns)
    else:
        # check that at least one raw column ends with "__q" for genesis + quality
        assert any(column.endswith("__q") for column in table.data.columns)


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
                "Unternehmen_(EU)__Anzahl",
                "Unternehmen_(EU)__q",
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
                "Lebensformen_am_Hauptwohnort__1000",
            ),
        ),
        (
            "6000F-1007",
            (5, 7),
            (
                "Stichtag",
                "Deutschland",
                "Ausstattung der Wohnung",
                "Familien__%",
                "Familien__%__q",
                "Familien__Anzahl",
                "Familien__Anzahl__q",
            ),
        ),
    ],
)
def test_get_data_with_quality_on_and_prettify_true(
    mocker, table_name: str, expected_shape: tuple[int, int], expected_columns: tuple[str]
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
                "Altersgruppen",
                "Bevoelkerung_in_Hauptwohnsitzhaushalten__1000",
                "Erwerbstaetige_aus_Hauptwohnsitzhaushalten__1000",
                "Erwerbslose_aus_Hauptwohnsitzhaushalten__1000",
                "Erwerbspersonen_aus_Hauptwohnsitzhaushalten__1000",
                "Nichterwerbspersonen_aus_Hauptwohnsitzhaushalten__1000",
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
                "Sozialvers.pflichtig_Beschaeftigte_am_Arbeitsort__Anzahl",
            ),
            "de",
        ),
        (
            "23111-0001",
            (32, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Krankenhaeuser__Anzahl",
                "Betten__Anzahl",
                "Betten_je_100.000_Einwohner__Anzahl",
                "Patienten__Anzahl",
                "Patienten_je_100.000_Einwohner__Anzahl",
                "Berechnungs-/Belegungstage__1000",
                "Durchschnittliche_Verweildauer__Tage",
                "Durchschnittliche_Bettenauslastung__Prozent",
            ),
            "de",
        ),
        (
            "23311-0010",
            (4352, 7),
            (
                "Jahr",
                "Herkunfts-Bundesland oder Ausland",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Quartale",
                "Familienstand",
                "Schwangerschaftsabbrueche__Anzahl",
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
                "Betriebe__Anzahl",
                "Erzeugte_Abfallmenge__1000_t",
                "Beschaeftigte__1000",
                "Erfassungsgrad_der_Betriebe__Prozent",
                "Erfassungsgrad_der_Beschaeftigten__Prozent",
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
                "Verwendung_klimawirksamer_Stoffe__t",
                "Verwendung_klimawirksamer_Stoffe_(CO2-Aequivalente)__1000_t",
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
                "Befoerderte_Personen__Anzahl",
                "Befoerderungsleistung__Person-km",
            ),
            "de",
        ),
        (
            "51000-0010",
            (262, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Länder",
                "Warenverzeichnis Außenhandelsstatistik (4-Steller)",
                "Ausfuhr:_Gewicht__t",
                "Ausfuhr:_Wert__Tsd._EUR",
                "Ausfuhr:_Wert_(US-Dollar)__Tsd._US_$",
                "Einfuhr:_Gewicht__t",
                "Einfuhr:_Wert__Tsd._EUR",
                "Einfuhr:_Wert_(US-Dollar)__Tsd._US_$",
            ),
            "de",
        ),
        (
            "61111-0021",
            (960, 5),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Monate",
                "Index_der_Nettokaltmieten__2020=100",
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
                "Erfasste_Haushalte__Anzahl",
                "Hochgerechnete_Haushalte__1000",
                "Durchschnittsbetrag_je_Haushalt_und_Monat__EUR",
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
                "Schulden_beim_nicht-oeffentlichen_Bereich__Mill._EUR",
            ),
            "de",
        ),
        (
            "91111-0001",
            (6600, 4),
            ("Jahr", "Deutschland insgesamt", "Indikatoren: Nachhaltige Entwicklung", "Indikatoren__jew._ME"),
            "de",
        ),
        (
            "11111-02-01-4",
            (538, 4),
            (
                "Stichtag",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Kreise und kreisfreie Städte",
                "Zahl_der_Gemeinden__Anzahl",
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
                "Studierende_(im_Kreisgebiet)__Anzahl",
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
                "Aufkommen_an_Haushaltsabfaellen_(o.E-altgeraete)__t",
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
                "Insolvenzverfahren_(Unternehmen)__MeasureUnitNotFound!",
                "Arbeitnehmer__Anzahl",
                "voraussichtliche_Forderungen_(Unternehmen)__Tsd._EUR",
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
                "Veraeusserungsfaelle_von_Bauland__Anzahl",
                "Veraeusserte_Baulandflaeche__1000_qm",
                "Kaufsumme__Tsd._EUR",
                "Durchschnittlicher_Kaufwert_je_qm__EUR",
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
                "Lohn-_und_Einkommensteuerpflichtige__Anzahl",
                "Gesamtbetrag_der_Einkuenfte__Tsd._EUR",
                "Lohn-_und_Einkommensteuer__Tsd._EUR",
            ),
            "de",
        ),
        (
            "86000U-Z-01",
            (2052, 7),
            (
                "Jahr",
                "Amtlicher Gemeindeschlüssel (AGS)",
                "Bundesländer",
                "Umweltbezogene Steuern",
                "Umweltbezogene_Steuern__Tsd._EUR",
                "Umweltbezogene_Steuern,_Index_(2010=100)__2010=100",
                "Umweltbezogene_Steuern,_Anteil_an_Summe_der_Laender__Prozent",
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
                "Anteil_Siedlungs-_und_Verkehrsflaeche_an_Gesamtflaeche__Prozent",
                "Veraenderung_der_Siedlungs-_und_Verkehrsflaeche__Prozent",
            ),
            "de",
        ),
        (
            "1000A-0001",
            (11339, 6),
            (
                "Stichtag",
                "Amtlicher Regionalschlüssel (ARS)",
                "Gemeinden",
                "Bevölkerungsdichte__Ew/qkm",
                "Fläche__qkm",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "2000S-2003",
            (110, 5),
            (
                "Stichtag",
                "Deutschland",
                "Erwerbsstatus",
                "Gebäudetyp (Größe)",
                "Personen__Anzahl",
            ),
            "de",
        ),
        (
            "3000G-1008",
            (7, 5),
            (
                "Stichtag",
                "Deutschland",
                "Heizungsart",
                "Gebäude mit Wohnraum__%",
                "Gebäude mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "4000W-5003",
            (4950, 8),
            (
                "Stichtag",
                "Deutschland",
                "Größe des privaten Haushalts",
                "Art der Wohnungsnutzung",
                "Ausstattung der Wohnung",
                "Fläche der Wohnung (20 m²-Intervalle)",
                "Art des Gebäudes",
                "Wohnungen in Gebäuden mit Wohnraum__Anzahl",
            ),
            "de",
        ),
        (
            "81000-0001",
            (40, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Preisbasis",
                "Bruttowertschoepfung__jew._ME",
                "Guetersteuern_abzuegl._Guetersubventionen__jew._ME",
                "Guetersteuern__jew._ME",
                "Guetersubventionen__jew._ME",
                "Bruttoinlandsprodukt__jew._ME",
                "nachr.:_Bruttoinlandsprodukt_(Veraenderung_in_%)__Prozent",
                "nachr.:_Bruttoinlandsprodukt_je_Einwohner__jew._ME",
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
                "Age groups",
                "Population_in_primary_residence_households__1000",
                "Persons_in_employment_from_primary_residence_hh.__1000",
                "Unemployed_persons_from_primary_residence_hh.__1000",
                "Economically_active_population_from_prim.resid.hh.__1000",
                "Economically_inactive_population_fr.prim.resid.hh.__1000",
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
                "Employees_subj._to_social_insur._at_place_of_work__number",
            ),
            "en",
        ),
        (
            "23111-0001",
            (32, 10),
            (
                "Year",
                "Germany",
                "Hospitals__number",
                "Beds__number",
                "Beds_per_100_000_inhabitants__number",
                "Patients__number",
                "Patients_per_100_000_inhabitants__number",
                "Occupancy_/_billing_days__1000",
                "Average_length_of_stay__days",
                "Average_occupancy_of_hospital_beds__percent",
            ),
            "en",
        ),
        (
            "23311-0010",
            (4352, 7),
            (
                "Year",
                "Land of origin or origin from abroad",
                "Official municipality key (AGS)",
                "Länder",
                "Quarters",
                "Marital status",
                "Terminations_of_pregnancy__number",
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
                "Local_units__number",
                "Quantity_of_waste_produced__1000_t",
                "Persons_employed__1000",
                "Coverage_of_local_units__percent",
                "Coverage_of_persons_employed__percent",
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
                "Use_of_climate-affecting_substances__t",
                "Use_of_climate-affecting_substances_(CO2-equiv.)__1000_t",
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
                "Passengers_carried__number",
                "Transport_performance__Person-km",
            ),
            "en",
        ),
        (
            "51000-0010",
            (262, 10),
            (
                "Year",
                "Germany",
                "Countries",
                "Commodity Class. Foreign Trade Stat.(4-digit cod.)",
                "Exports:_Net_mass__t",
                "Exports:_Value__Tsd._EUR",
                "Exports:_Value_(US-Dollar)__Tsd._US_$",
                "Imports:_Net_mass__t",
                "Imports:_Value__Tsd._EUR",
                "Imports:_Value_(US-Dollar)__Tsd._US_$",
            ),
            "en",
        ),
        (
            "61111-0021",
            (960, 5),
            (
                "Year",
                "Official municipality key (AGS)",
                "Länder",
                "Months",
                "Index_of_net_rents_exclusive_of_heating_expenses__2020=100",
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
                "Households_covered__number",
                "Households_extrapolated__1000",
                "Average_amount_per_household_and_month__EUR",
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
                "Debts_owed_to_the_non-public_sector__Mill._EUR",
            ),
            "en",
        ),
        (
            "91111-0001",
            (6600, 4),
            ("Year", "Germany", "Indicators: Sustainable development", "Indicators__jew._ME"),
            "en",
        ),
        (
            "1000A-0001",
            (11339, 6),
            (
                "Reference date",
                "Official regional key (ARS)",
                "Municipalities (LAU-2)",
                "Area__Unknown_Unit",
                "Persons__number",
                "Population density__Unknown_Unit",
            ),
            "en",
        ),
        (
            "2000S-2003",
            (110, 5),
            (
                "Reference date",
                "Germany",
                "Activity status (detailed)",
                "Type of the building (size)",
                "Persons__number",
            ),
            "en",
        ),
        (
            "3000G-1008",
            (7, 5),
            (
                "Reference date",
                "Germany",
                "Type of heating",
                "Buildings with residential space__%",
                "Buildings with residential space__number",
            ),
            "en",
        ),
        (
            "4000W-5003",
            (4950, 8),
            (
                "Reference date",
                "Germany",
                "Size of private household",
                "Type of use of the dwelling",
                "Equipment in dwelling",
                "Floor area of the dwelling (20m² intervals)",
                "Type of building",
                "Dwellings in buildings with residential space__number",
            ),
            "en",
        ),
    ],
)
def test_prettify(mocker, table_name, expected_shape: tuple[int, int], expected_columns: tuple[str], language: str):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True, language=language)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns
