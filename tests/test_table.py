import os

import pandas as pd
import pytest

import pystatis

pystatis.clear_cache()


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape",
    [
        ("12211-0001", (45, 22)),
        ("13111-0005", (384, 14)),
        ("23111-0001", (32, 17)),
        ("23311-0010", (4352, 22)),
        ("32161-0003", (14, 18)),
        ("32421-0012", (560, 19)),
        ("46181-0001", (8, 19)),
        ("51000-0010", (262, 23)),
        ("61111-0021", (960, 14)),
        ("63121-0001", (180, 20)),
        ("71311-0001", (600, 22)),
        ("91111-0001", (6600, 14)),
        ("11111-02-01-4", (538, 10)),
        ("13111-01-03-4", (3228, 18)),
        ("21311-01-01-4-B", (44010, 22)),
        ("32121-01-02-4", (3766, 14)),
        ("41312-01-01-4", (5918, 14)),
        ("52411-02-01-4", (538, 12)),
        ("61511-01-03-4", (1076, 17)),
        ("73111-01-01-4", (538, 12)),
        ("86000U-Z-01", (2052, 16)),
        ("AI-N-01-2-5", (13922, 11)),
        ("1000A-0001", (34017, 13)),
        ("2000S-2003", (110, 21)),
        ("3000G-1008", (14, 17)),
        ("4000W-5003", (4950, 33)),
    ],
)
def test_get_data(mocker, table_name: str, expected_shape: tuple[int, int]):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=False)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty
    assert isinstance(table.raw_data, str)
    assert table.raw_data != ""

    assert table.data.shape == expected_shape


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "table_name, expected_shape, expected_columns",
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
        ),
        (
            "13111-0005",
            (384, 4),
            ("Stichtag", "Bundesländer", "Geschlecht", "Sozialvers.pflichtig_Beschaeftigte_am_Arbeitsort__Anzahl"),
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
        ),
        (
            "23311-0010",
            (4352, 6),
            (
                "Jahr",
                "Herkunfts-Bundesland oder Ausland",
                "Bundesländer",
                "Quartale",
                "Familienstand",
                "Schwangerschaftsabbrueche__Anzahl",
            ),
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
        ),
        (
            "32421-0012",
            (560, 6),
            (
                "Jahr",
                "Bundesländer",
                "Stoffgruppen",
                "Einsatzbereiche",
                "Verwendung_klimawirksamer_Stoffe__t",
                "Verwendung_klimawirksamer_Stoffe_(CO2-Aequivalente)__1000_t",
            ),
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
        ),
        ("61111-0021", (960, 4), ("Jahr", "Bundesländer", "Monate", "Index_der_Nettokaltmieten__2020=100")),
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
        ),
        (
            "91111-0001",
            (6600, 4),
            ("Jahr", "Deutschland insgesamt", "Indikatoren: Nachhaltige Entwicklung", "Indikatoren__jew._ME"),
        ),
        (
            "11111-02-01-4",
            (538, 3),
            ("Stichtag", "Kreise und kreisfreie Städte", "Zahl_der_Gemeinden__Anzahl"),
        ),
        (
            "13111-01-03-4",
            (3228, 5),
            (
                "Stichtag",
                "Kreise und kreisfreie Städte",
                "Nationalität",
                "Geschlecht",
                "Sozialversicherungspfl._Beschaeftigte_(Arbeitsort)__Anzahl",
            ),
        ),
        (
            "21311-01-01-4-B",
            (44010, 6),
            (
                "Semester",
                "Kreise und kreisfreie Städte",
                "Geschlecht",
                "Nationalität (inkl. insgesamt)",
                "Fächergruppe (mit Insgesamt)",
                "Studierende_(im_Kreisgebiet)__Anzahl",
            ),
        ),
        (
            "32121-01-02-4",
            (3766, 4),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Abfallarten von Haushaltsabfällen",
                "Aufkommen_an_Haushaltsabfaellen_(o.E-altgeraete)__t",
            ),
        ),
        ("41312-01-01-4", (5918, 4), ("Stichtag", "Kreise und kreisfreie Städte", "Tierarten", "Tiere__Anzahl")),
        (
            "52411-02-01-4",
            (538, 5),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Insolvenzverfahren_(Unternehmen)__MeasureUnitNotFound!",
                "Arbeitnehmer__Anzahl",
                "voraussichtliche_Forderungen_(Unternehmen)__Tsd._EUR",
            ),
        ),
        (
            "61511-01-03-4",
            (1076, 7),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Baulandverkäufe",
                "Veraeusserungsfaelle_von_Bauland__Anzahl",
                "Veraeusserte_Baulandflaeche__1000_qm",
                "Kaufsumme__Tsd._EUR",
                "Durchschnittlicher_Kaufwert_je_qm__EUR",
            ),
        ),
        (
            "73111-01-01-4",
            (538, 5),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Lohn-_und_Einkommensteuerpflichtige__Anzahl",
                "Gesamtbetrag_der_Einkuenfte__Tsd._EUR",
                "Lohn-_und_Einkommensteuer__Tsd._EUR",
            ),
        ),
        (
            "86000U-Z-01",
            (2052, 6),
            (
                "Jahr",
                "Bundesländer",
                "Umweltbezogene Steuern",
                "Umweltbezogene_Steuern__Tsd._EUR",
                "Umweltbezogene_Steuern,_Index_(2010=100)__2010=100",
                "Umweltbezogene_Steuern,_Anteil_an_Summe_der_Laender__Prozent",
            ),
        ),
        (
            "AI-N-01-2-5",
            (13922, 4),
            (
                "Jahr",
                "Gemeinden",
                "Anteil_Siedlungs-_und_Verkehrsflaeche_an_Gesamtflaeche__Prozent",
                "Veraenderung_der_Siedlungs-_und_Verkehrsflaeche__Prozent",
            ),
        ),
        (
            "1000A-0001",
            (11339, 5),
            ("Stichtag", "Gemeinden", "Bevölkerungsdichte__Ew/qkm", "Fläche__qkm", "Personen__Anzahl"),
        ),
        (
            "2000S-2003",
            (110, 5),
            ("Stichtag", "Deutschland", "Erwerbsstatus", "Gebäudetyp (Größe)", "Personen__Anzahl"),
        ),
        (
            "3000G-1008",
            (7, 5),
            ("Stichtag", "Deutschland", "Heizungsart", "Gebäude mit Wohnraum__%", "Gebäude mit Wohnraum__Anzahl"),
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
        ),
    ],
)
def test_prettify(mocker, table_name, expected_shape: tuple[int, int], expected_columns: tuple[str]):
    mocker.patch.object(pystatis.db, "check_credentials", return_value=True)
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns
