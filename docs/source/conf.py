import os
import sys
sys.path.insert(0, os.path.abspath('../../pypergraph/'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Pypergraph'
copyright = '2025, Michael Brummer Ringdal'
author = 'Michael Brummer Ringdal'
release = '0.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_design',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # For Google and NumPy style docstrings
    # 'sphinx_rtd_dark_mode',
]

templates_path = ['_templates']
exclude_patterns = []

# user starts in dark mode
# default_dark_mode = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
