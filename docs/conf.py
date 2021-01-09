# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../python-api"))
sys.path.insert(0, root_path)
sys.setrecursionlimit(1500)

# -- Project information -----------------------------------------------------

project = "Wisconsin Autonomous Simulator"
copyright = "2021, Wisconsin Autonomous"
author = "Wisconsin Autonomous"

# The full version, including alpha/beta/rc tags
release = "0.0.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "rinoh.frontend.sphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "m2r2",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_favicon = "_static/wa-dark-favicon.png"
html_theme_options = {
    "announcement": """
        <a style=\"text-decoration: none; color: white;\" 
           href=\"https://wisconsinautonomous.org\">
           <img src=\"https://github.com/WisconsinAutonomous/wa-resources/blob/master/Images/wa-dark.png?raw=true\" 
                style=\"vertical-align: middle; display: inline; padding-right: 7.5px; height: 20px;\"/>
           Checkout our website!
        </a>
    """,
    "sidebar_hide_name": True,
    "light_logo": "wa-light.png",
    "dark_logo": "wa-dark.png",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]