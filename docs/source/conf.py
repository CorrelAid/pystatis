# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from pathlib import Path

import tomllib

project = "pystatis"
copyright = "2022, Michael Aydinbas"
authors = [
    "Michael Aydinbas <michael.aydinbas@gmail.com>",
    "Ariz Weber <ariz.weber@protonmail.com>",
    "CorrelAid <info@correlaid.org>",
    "Daniel Pleus <danielpleus@gmail.com>",
    "Felix Schmitz <felix.schmitz@philosophy-economics.de>",
    "Frederik Hering <jobs.fhering@gmail.com>",
    "Marco Hübner <marco_huebner1@gmx.de>",
]
maintainers = ["Michael Aydinbas <michael.aydinbas@gmail.com>"]

# Read version from pyproject.toml
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    pyproject_data = tomllib.load(f)

release = pyproject_data["project"]["version"]
version = release


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "nbsphinx",
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",  # used to generate overview tables
    "sphinx.ext.napoleon",  # used for google-style docstrings
]

templates_path = ["_templates"]
exclude_patterns = []
nbsphinx_execute = "never"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_title = "pystatis"
html_short_title = "pystatis documentation"
html_logo = "_static/pystatis_logo.png"
html_favicon = "_static/pystatis_logo.ico"
autodoc_typehints = "description"
