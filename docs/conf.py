#!/usr/bin/env python

from chaturbate_poller import __version__

project = "chaturbate_poller"
project_copyright = "2024, MountainGod2"
author = "MountainGod2"
extensions: list[str] = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]
version: str = __version__
release: str = __version__
napoleon_google_docstring = True
napoleon_numpy_docstring = False
autoapi_dirs: list[str] = ["../src"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
# Ignore specific URLs during link checking
linkcheck_ignore: list[str] = [
    "https://chaturbate.com/statsapi/authtoken/",
    # Ignore GitHub commits, pull requests, and issues
    r"https://github\.com/MountainGod2/chaturbate_poller/commit/[0-9a-f]+",
    r"https://github\.com/MountainGod2/chaturbate_poller/pull/\d+",
    r"https://github\.com/MountainGod2/chaturbate_poller/issues/\d+",
    # Ignore localhost URLs
    r"http://localhost:\d+",
    # Ignore local file paths
    r"file://.*",
]
