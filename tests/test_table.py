import pandas as pd
import pytest

import pystatis


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
        ("12111-01-01-4", (4842, 18)),
        ("21311-01-01-4-B", (44010, 22)),
        ("32121-01-02-4", (3766, 14)),
        ("41312-01-01-4", (5918, 14)),
        ("52411-02-01-4", (538, 12)),
        ("61511-01-03-4", (1076, 17)),
        ("73111-01-01-4", (538, 12)),
        ("86000U-Z-01", (2052, 16)),
        ("AI-N-01-2-5", (13922, 11)),
    ],
)
def test_get_data(table_name: str, expected_shape: tuple[int, int]):
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
                "Bevoelkerung_in_Hauptwohnsitzhaushalten",
                "Erwerbstaetige_aus_Hauptwohnsitzhaushalten",
                "Erwerbslose_aus_Hauptwohnsitzhaushalten",
                "Erwerbspersonen_aus_Hauptwohnsitzhaushalten",
                "Nichterwerbspersonen_aus_Hauptwohnsitzhaushalten",
            ),
        ),
        (
            "13111-0005",
            (384, 4),
            ("Stichtag", "Bundesländer", "Geschlecht", "Sozialvers.pflichtig_Beschaeftigte_am_Arbeitsort"),
        ),
        (
            "23111-0001",
            (32, 10),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Krankenhaeuser",
                "Betten",
                "Betten_je_100.000_Einwohner",
                "Patienten",
                "Patienten_je_100.000_Einwohner",
                "Berechnungs-/Belegungstage",
                "Durchschnittliche_Verweildauer",
                "Durchschnittliche_Bettenauslastung",
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
                "Schwangerschaftsabbrueche",
            ),
        ),
        (
            "32161-0003",
            (14, 8),
            (
                "Jahr",
                "Deutschland insgesamt",
                "WZ2008 (2-Steller): Abfallerzeugung",
                "Betriebe",
                "Erzeugte_Abfallmenge",
                "Beschaeftigte",
                "Erfassungsgrad_der_Betriebe",
                "Erfassungsgrad_der_Beschaeftigten",
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
                "Verwendung_klimawirksamer_Stoffe",
                "Verwendung_klimawirksamer_Stoffe_(CO2-Aequivalente)",
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
                "Befoerderte_Personen",
                "Befoerderungsleistung",
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
                "Ausfuhr:_Gewicht",
                "Ausfuhr:_Wert",
                "Ausfuhr:_Wert_(US-Dollar)",
                "Einfuhr:_Gewicht",
                "Einfuhr:_Wert",
                "Einfuhr:_Wert_(US-Dollar)",
            ),
        ),
        ("61111-0021", (960, 4), ("Jahr", "Bundesländer", "Monate", "Index_der_Nettokaltmieten")),
        (
            "63121-0001",
            (180, 7),
            (
                "Jahr",
                "Deutschland insgesamt",
                "Haushaltsgröße",
                "Einnahme- und Ausgabearten",
                "Erfasste_Haushalte",
                "Hochgerechnete_Haushalte",
                "Durchschnittsbetrag_je_Haushalt_und_Monat",
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
                "Schulden_beim_nicht-oeffentlichen_Bereich",
            ),
        ),
        (
            "91111-0001",
            (6600, 4),
            ("Jahr", "Deutschland insgesamt", "Indikatoren: Nachhaltige Entwicklung", "Indikatoren"),
        ),
        (
            "11111-02-01-4",
            (538, 3),
            ("Stichtag", "Kreise und kreisfreie Städte", "Zahl_der_Gemeinden"),
        ),
        (
            "12111-01-01-4",
            (4842, 5),
            ("Stichtag", "Kreise und kreisfreie Städte", "Nationalität", "Geschlecht", "Bevoelkerung"),
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
                "Studierende_(im_Kreisgebiet)",
            ),
        ),
        (
            "32121-01-02-4",
            (3766, 4),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Abfallarten von Haushaltsabfällen",
                "Aufkommen_an_Haushaltsabfaellen_(o.E-altgeraete)",
            ),
        ),
        ("41312-01-01-4", (5918, 4), ("Stichtag", "Kreise und kreisfreie Städte", "Tierarten", "Tiere")),
        (
            "52411-02-01-4",
            (538, 5),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Insolvenzverfahren_(Unternehmen)",
                "Arbeitnehmer",
                "voraussichtliche_Forderungen_(Unternehmen)",
            ),
        ),
        (
            "61511-01-03-4",
            (1076, 7),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Baulandverkäufe",
                "Veraeusserungsfaelle_von_Bauland",
                "Veraeusserte_Baulandflaeche",
                "Kaufsumme",
                "Durchschnittlicher_Kaufwert_je_qm",
            ),
        ),
        (
            "73111-01-01-4",
            (538, 5),
            (
                "Jahr",
                "Kreise und kreisfreie Städte",
                "Lohn-_und_Einkommensteuerpflichtige",
                "Gesamtbetrag_der_Einkuenfte",
                "Lohn-_und_Einkommensteuer",
            ),
        ),
        (
            "86000U-Z-01",
            (2052, 6),
            (
                "Jahr",
                "Bundesländer",
                "Umweltbezogene Steuern",
                "Umweltbezogene_Steuern",
                "Umweltbezogene_Steuern,_Index_(2010=100)",
                "Umweltbezogene_Steuern,_Anteil_an_Summe_der_Laender",
            ),
        ),
        (
            "AI-N-01-2-5",
            (13922, 4),
            (
                "Jahr",
                "Gemeinden",
                "Anteil_Siedlungs-_und_Verkehrsflaeche_an_Gesamtflaeche",
                "Veraenderung_der_Siedlungs-_und_Verkehrsflaeche",
            ),
        ),
    ],
)
def test_prettify(table_name, expected_shape: tuple[int, int], expected_columns: tuple[str]):
    table = pystatis.Table(name=table_name)
    table.get_data(prettify=True)

    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty

    assert table.data.shape == expected_shape
    assert tuple(table.data.columns) == expected_columns
