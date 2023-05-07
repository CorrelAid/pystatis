# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pystatis'
copyright = '2023, Michael Aydinbas'
authors = [
    "Michael Aydinbas <michael.aydinbas@gmail.com>",
    "Ariz Weber <ariz.weber@protonmail.com>",
    "CorrelAid <info@correlaid.org>",
    "Daniel Pleus <danielpleus@gmail.com>",
    "Felix Schmitz <felix.schmitz@philosophy-economics.de>",
    "Frederik Hering <jobs.fhering@gmail.com>",
    "Marco Hübner <marco_huebner1@gmx.de>"
]
maintainers = [
    "Michael Aydinbas <michael.aydinbas@gmail.com>"
]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
