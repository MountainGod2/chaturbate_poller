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
]
version: str = __version__
release: str = __version__
napoleon_google_docstring = True
napoleon_numpy_docstring = False
autoapi_dirs: list[str] = ["../src"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
# Ignore specific URLs during link checking
linkcheck_ignore = [
    "https://chaturbate.com/statsapi/authtoken/",
    # Ignore GitHub commits
    r"https://github\.com/MountainGod2/chaturbate_poller/commit/[0-9a-f]+",
    # Ignore GitHub pull requests
    r"https://github\.com/MountainGod2/chaturbate_poller/pull/\d+",
    # Ignore GitHub issues
    r"https://github\.com/MountainGod2/chaturbate_poller/issues/\d+",
]
