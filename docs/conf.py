# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("../"))

project = "crease-shapes"
copyright = "2025, Vaibhav Venkat"
author = "Vaibhav Venkat"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/shapes_3d/objects"]
autodoc_mock_imports = ["shapes_3d.objects"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
autodoc_default_options = {
    "exclude-members": "shapes_3d.objects",  # Exclude unwanted submodules or members
}
html_theme = "sphinx_rtd_theme"
html_css_files = ["css/main.css"]
html_static_path = ["_static"]
