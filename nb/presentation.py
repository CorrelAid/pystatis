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
# After running `.run()` for the first time, we can also print a summary, using `.summary()`

# %%
results.summary()

# %% [markdown]
# If interested in specific object, can run `results.tables`, `results.statistics`, or `results.variables` directly.

# %%
results.tables

# %% [markdown]
# Add `.df` to convert to a dataframe for easier handling.

# %%
results.tables.df 

# %% [markdown]
# We can then access the relevant codes with `.get_code([#])`. Doing this returns a list of codes from specified rows which may be useful to run in the Table method.

# %%
results.tables.get_code([0,1,2]) 

# %% [markdown]
# To then check that the object has the relevant data, we can preview the columns using the `.meta_data()` method.

# %%
results.tables.get_metadata([1,2])

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
t = pystatis.Table(name="71327-01-05-4")
t.get_data()
t.data

# %%
# Zensus
t = pystatis.Table(name="2000S-1006")
t.get_data()
t.data

# %% [markdown]
# The `get_data()` method supports all parameters that you can pass to the API, like `startyear`, `endyear` or `timeslicec`

# %%
# GENESIS
t = pystatis.Table(name="43311-0001")
t.get_data(startyear=2000)
t.data
