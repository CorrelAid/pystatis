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

# %%

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
t = pystatis.Table(name="71321-0001")
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
