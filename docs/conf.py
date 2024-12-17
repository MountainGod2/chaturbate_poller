#!/usr/bin/env python

from chaturbate_poller import __version__

project = "chaturbate_poller"
project_copyright = "2024, MountainGod2"
author = "MountainGod2"
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
version = __version__
release = __version__
myst_enable_extensions = ["linkify"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False
autoapi_dirs = ["../src"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
