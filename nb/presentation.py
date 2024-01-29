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
# ### Table

# %%
t = pystatis.Table(name="32111-01-01-4")

# %%
t.get_data()

# %%
t.data

# %%
t.raw_data.splitlines()

# %%
pprint(t.metadata)

# %%
t = pystatis.Table(name="12111-01-01-5-B")

# %%
# runs for roughly 2 minutes
t.get_data()  # GENESIS starts a backghround job and we wait 3000 seconds -> no action required

# %%
t.data  # 122058 x 18 columns
