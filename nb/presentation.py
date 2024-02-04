# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: pystatis
#     language: python
#     name: python3
# ---

# %%
from pprint import pprint

import pystatis

# %% [markdown]
# # CorrelAid
#
# https://www.correlaid.org/en/about/
#
# ## Our Mission
#
# CorrelAid is a **non-profit community of data science enthusiasts** who want to change the world using data science. We dedicate our work to the humans, initiatives and organizations that strive to make the world a better place.
#
# We value open knowledge management and transparency in our work wherever possible while complying with GDPR regulations and following strong principles of data ethics.
#
# ## Our Work
#
# Our work is based on three pillars:
#
# 1. **Using data**: We enable data analysts and scientists to apply their knowledge for the common good and social organizations to increase their impact on society by **conducting pro-bono data for good (Data4Good) projects** and providing consulting on data topics.
# 2. **Education**: We strongly believe in sharing our knowledge. It is not for nothing that we have chosen "education" as our association's official purpose. This is why we offer numerous education formats for nonprofits and volunteers. In addition, we share our knowledge, code, and materials publicly.
# 3. **Community**: Our community is the basis of our work. We unite data scientists of different backgrounds and experience levels. We organize ourselves both online and on-site within our CorrelAidX local groups.

# %% [markdown]
# # Pystatis presentation
#
# `pystatis` is a small Python library to conveniently wrap the different GENESIS web services (APIs) in a centralized and user-friendly manner.
#
# It allows users to browse the different databases and download the desired tables from all supported databases in a convenient `pandas` `DataFrame` object, suited for further analysis.

# %% [markdown]
# ## Setup
#
# We won't cover the initial only-once setup here because the user has to enter their credentials for the supported databases (GENESIS, Regionalstatistik, Zensus). But there is a dedicated notebook [Setup](./00_Setup.ipynb) with examples and explanations.

# %% [markdown]
# ## Main Use Cases

# %% [markdown]
# ### Find

# %% [markdown]
# `pystatis.Find` allows a user to use a keyword to browse the data available on the chosen database. Finds 3 different objects:
# - Tables: the tables containing the relevant keyword in title
# - Statistics: statistics is the larger collections of tables on the topic, finds the ones with keyword in title
# - Variables: variables are the values (DE: Merkmal) in columns of the tables, find ones with keyword in label
#
# Returns the titles of relevant tables/statistics/variables and their [EVAS](https://www.destatis.de/DE/Service/Bibliothek/Abloesung-Fachserien/uebersicht-fs.html) number – useful tool to look these up (EVAS is necessary for the Table method)
#
# 1. call Find using a keyword `query=<keyword>` and specifying a database `db_name=<genesis|zensus|regio>`
# 2. actually query the API and print the results using `.run()`
# 3. access the various objects, their EVAS numbers, or preview using metadata

# %%
results = pystatis.Find(query="Abfall", db_name="regio")
results.run()

# %% [markdown]
# If interested in specific object, can run `results.tables`, `results.statistics`, or `results.variables` directly.

# %% [markdown]
#

# %%
results.tables

# %% [markdown]
# Add `.df` to convert to a dataframe for easier handling.

# %%
results.tables.df

# %% [markdown]
# We can then access the relevant codes with `.get_code([#])`. Doing this returns a list of codes from specified rows which may be useful to run in the Table method.

# %%
results.tables.get_code([0, 1, 2])

# %% [markdown]
# To then check that the object has the relevant data, we can preview the columns using the `.meta_data()` method.

# %%
results.tables.get_metadata([1, 2])

# %% [markdown]
# The `pystatis.Find` is a useful search tool to browse the database by any keyword. It is quicker than downloading a table and does not need the EVAS number to run.
#
# Use this to identify the tables of interest and to look up their EVAS as to use in the further analysis with a `pystatis.Table` method.

# %% [markdown]
# ### Table

# %% [markdown]
# `pystatis.Table` offers a simple Interface to get any table via its "name" ([EVAS](https://www.destatis.de/DE/Service/Bibliothek/Abloesung-Fachserien/uebersicht-fs.html) number).
#
# 1. Create a new Table instance by passing `name=<EVAS>`
# 2. Download the actual data with `.get_data(prettify=<True|False>)`
# 3. Access data via either `.raw_data` or `.data`, metadata via `.metadata`

# %%
# GENESIS - https://www-genesis.destatis.de/genesis//online?operation=table&code=31231-0001&bypass=true&levelindex=1&levelid=1706599948340#abreadcrumb
t = pystatis.Table(name="31231-0001")  #

# %% [markdown]
# Per default, `prettify` is set to `True` and will return a more readable format. Here we show the original format first.

# %%
t.get_data(prettify=False)

# %%
t.raw_data.splitlines()

# %%
t.data

# %% [markdown]
# As you can see, the original format has a lot of redundant information and columns with metadata like the codes for the different variables. Let's rerun `get_data` with `prettify=True`.

# %%
t.get_data()

# %%
t.data

# %% [markdown]
# You can also access the metadata as returned by the Catalogue endpoint.

# %%
pprint(t.metadata)

# %% [markdown]
# You can use any EVAS number from the supported databases like GENESIS, Regionalstatistik or Zensus. The library identifies the database for you so you don't have to care about this.

# %%
# GENESIS
t = pystatis.Table(name="43311-0001")
t.get_data()
t.data

# %%
# Regionalstatistik
t = pystatis.Table(name="21311-01-01-4")
t.get_data()
t.data

# %%
# Zensus
t = pystatis.Table(name="2000S-1006")
t.get_data()
t.data

# %% [markdown]
# The `get_data()` method supports all parameters that you can pass to the API, like `startyear`, `endyear` or `timeslices`

# %%
# GENESIS
t = pystatis.Table(name="43311-0001")
t.get_data(startyear=2000)
t.data

# %% [markdown]
# ## Advanced features
#
# - Caching
# - Handling background jobs
# - Cubes

# %% [markdown]
# ## Geo-visualization

# %% [markdown]
# Case study: international students in Germany
# - time evolution
# - regional differences (at the level of federal states)

# %%
# # !pip install geopandas
# # !pip install matplotlib

# %%
import geopandas
import pandas as pd
from matplotlib import pyplot as plt

# %% [markdown]
# ### load data from Regionalstatistik

# %%
students = pystatis.Table(name="21311-01-01-4")

# %%
students.get_data(startyear=2015)

# %% [markdown]
# ### set proper column types

# %%
students.data["Kreise und kreisfreie Städte_Code"] = students.data[
    "Kreise und kreisfreie Städte_Code"
].astype(str)
students.data["Kreise und kreisfreie Städte_Code"]

# %%
students.data["Kreise und kreisfreie Städte_Code"] = students.data[
    "Kreise und kreisfreie Städte_Code"
].apply(lambda x: "0" + x if len(x) <= 1 else x)
students.data["Kreise und kreisfreie Städte_Code"]

# %% [markdown]
# ### Dataframe

# %%
students.data

# %% [markdown]
# ### determine ratio of international students per year and region

# %%
ratio_international = (
    students.data[
        (students.data.Geschlecht == "Insgesamt")
        & (students.data["Fächergruppe (mit Insgesamt)"] == "Insgesamt")
    ]
    .groupby(
        by=[
            "Kreise und kreisfreie Städte",
            "Kreise und kreisfreie Städte_Code",
            "Semester",
        ]
    )["Studierende_(im_Kreisgebiet)"]
    .apply(lambda x: x.iloc[1] / x.iloc[0] if x.count() == 3 else None)
)
ratio_international.rename("ratio_international", inplace=True)

ratio_international = pd.DataFrame(ratio_international)
ratio_international["year"] = [
    int(semester[3:7])
    for semester in ratio_international.index.get_level_values(2)
]

ratio_international

# %%
ratio_international[ratio_international.index.get_level_values(0) == "  Bayern"]

# %% [markdown]
# ## plot time evolution

# %%
for region in [
    "Deutschland",
    "  Baden-Württemberg",
    "  Bayern",
    "  Nordrhein-Westfalen",
    "  Thüringen",
    "  Sachsen",
    "  Niedersachsen",
    "  Schleswig-Holstein",
    "  Berlin",
]:
    plt.plot(
        ratio_international[
            ratio_international.index.get_level_values(0) == region
        ].year,
        ratio_international[
            ratio_international.index.get_level_values(0) == region
        ].ratio_international,
        label=region,
    )
plt.legend()

# %% [markdown]
# ### load shape file

# %%

path_to_data = "./data/VG2500_LAN.shp"
gdf = geopandas.read_file(path_to_data)


# %%
gdf.loc[:, "area"] = gdf.area

# %%
gdf.plot("area", legend=True)

# %%
gdf.GEN

# %%
gdf.AGS = gdf.AGS.astype(str)

# %% [markdown]
# ### merge with geodataframe and plot

# %%
fig = plt.figure(figsize=(10, 5))

ax1 = fig.add_subplot(131)
year = 2015
plt.title(str(year))
gdf_merged = pd.merge(
    left=gdf,
    right=ratio_international[ratio_international.year == year],
    left_on="AGS",
    right_on="Kreise und kreisfreie Städte_Code",
)
gdf_merged.ratio_international
gdf_merged.plot(
    "ratio_international",
    ax=ax1,
    legend=True,
    missing_kwds={"color": "lightgrey"},
    legend_kwds={
        "label": "ratio of int. students",
        "orientation": "horizontal",
    },
    vmin=0.08,
    vmax=0.23,
)

ax2 = fig.add_subplot(132)
year = 2018
plt.title(str(year))
gdf_merged = pd.merge(
    left=gdf,
    right=ratio_international[ratio_international.year == year],
    left_on="AGS",
    right_on="Kreise und kreisfreie Städte_Code",
)
gdf_merged.ratio_international
gdf_merged.plot(
    "ratio_international",
    ax=ax2,
    legend=True,
    missing_kwds={"color": "lightgrey"},
    legend_kwds={
        "label": "ratio of int. students",
        "orientation": "horizontal",
    },
    vmin=0.08,
    vmax=0.23,
)

ax3 = fig.add_subplot(133)
year = 2021
plt.title(str(year))
gdf_merged = pd.merge(
    left=gdf,
    right=ratio_international[ratio_international.year == year],
    left_on="AGS",
    right_on="Kreise und kreisfreie Städte_Code",
)
gdf_merged.ratio_international
gdf_merged.plot(
    "ratio_international",
    ax=ax3,
    legend=True,
    missing_kwds={"color": "lightgrey"},
    legend_kwds={
        "label": "ratio of int. students",
        "orientation": "horizontal",
    },
    vmin=0.08,
    vmax=0.23,
)

# %% [markdown]
# ## Outlook

# %% [markdown]
# - `quality=on`

# %% [markdown]
#
