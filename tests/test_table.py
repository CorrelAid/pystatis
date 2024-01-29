import pandas as pd
import pytest

import pystatis

EASY_TABLE = """Statistik_Code;Statistik_Label;Zeit_Code;Zeit_Label;Zeit;1_Merkmal_Code;1_Merkmal_Label;1_Auspraegung_Code;1_Auspraegung_Label;     FLC006__Gebietsflaeche__qkm
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;08;Baden-Württemberg;35747,85
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;09;Bayern;70541,58
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;11;Berlin;891,12
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;12;Brandenburg;29654,38
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;04;Bremen;419,61
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;02;Hamburg;755,09
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;06;Hessen;21115,62
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;13;Mecklenburg-Vorpommern;23294,90
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;03;Niedersachsen;47709,90
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;05;Nordrhein-Westfalen;34112,72
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;07;Rheinland-Pfalz;19857,97
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;10;Saarland;2571,52
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;14;Sachsen;18449,86
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;15;Sachsen-Anhalt;20467,20
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;01;Schleswig-Holstein;15804,30
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;16;Thüringen;16202,37
11111;Feststellung des Gebietsstands;STAG;Stichtag;31.12.2022;DLAND;Bundesländer;;Insgesamt;357595,99"""


def test_get_data(mocker):
    mocker.patch("pystatis.table.load_data", return_value=EASY_TABLE)
    table = pystatis.Table(name="11111-0001")
    table.get_data(prettify=False)
    assert table.data.shape == (17, 10)
    assert isinstance(table.data, pd.DataFrame)
    assert not table.data.empty
    assert isinstance(table.raw_data, str)
    assert table.raw_data != ""


def test_prettify(mocker):
    mocker.patch("pystatis.table.load_data", return_value=EASY_TABLE)
    table = pystatis.Table(name="11111-0001")
    table.get_data(prettify=True)
    assert table.data.shape == (17, 3)
    assert table.data.columns.to_list() == [
        "Stichtag",
        "Bundesländer",
        "Gebietsflaeche",
    ]
