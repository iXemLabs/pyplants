# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyplants'
copyright = '2026, iXemLabs'
author = 'iXemLabs'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static', '_static/custom.css']
html_sidebars = {
    '**': [
        'about.html',
        'searchbox.html',
        'navigation.html'
    ]
}
html_theme_options = {
    "description": " A collection of disease and phenology models for plants.",
    "fixed_sidebar": True,
    "github_user": "iXemLabs",
    "github_repo": "pyplants",
    "github_button": True
}
