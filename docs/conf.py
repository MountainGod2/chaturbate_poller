#!/usr/bin/env python

from chaturbate_poller import __version__

project = "chaturbate_poller"
project_copyright = "2025, MountainGod2"
author = "MountainGod2"
extensions: list[str] = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
]
version: str = __version__
release: str = __version__

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# AutoAPI settings
autoapi_dirs: list[str] = ["../src"]
autoapi_type = "python"
autoapi_template_dir = "_templates/autoapi"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_python_class_content = "both"
autoapi_member_order = "groupwise"
autoapi_root = "api"
autoapi_keep_files = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# MyST-NB settings
nb_execution_timeout = 60
nb_execution_allow_errors = False

exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"

# Enhanced theme options
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
    "logo_only": False,
}

coverage_show_missing_items = True

todo_include_todos = True

linkcheck_ignore: list[str] = [
    "https://chaturbate.com/statsapi/authtoken/",
    r"https://github\.com/.*",
    r"http://localhost:\d+",
    r"file://.*",
]


__all__ = [
    "author",
    "autoapi_dirs",
    "autoapi_dirs",
    "autoapi_keep_files",
    "autoapi_keep_files",
    "autoapi_member_order",
    "autoapi_member_order",
    "autoapi_options",
    "autoapi_options",
    "autoapi_python_class_content",
    "autoapi_python_class_content",
    "autoapi_root",
    "autoapi_root",
    "autoapi_template_dir",
    "autoapi_template_dir",
    "autoapi_type",
    "autoapi_type",
    "coverage_show_missing_items",
    "exclude_patterns",
    "extensions",
    "html_theme",
    "html_theme_options",
    "intersphinx_mapping",
    "intersphinx_mapping",
    "linkcheck_ignore",
    "linkcheck_ignore",
    "napoleon_attr_annotations",
    "napoleon_google_docstring",
    "napoleon_include_init_with_doc",
    "napoleon_include_private_with_doc",
    "napoleon_include_special_with_doc",
    "napoleon_numpy_docstring",
    "napoleon_preprocess_types",
    "napoleon_type_aliases",
    "napoleon_use_admonition_for_examples",
    "napoleon_use_admonition_for_notes",
    "napoleon_use_admonition_for_references",
    "napoleon_use_ivar",
    "napoleon_use_param",
    "napoleon_use_rtype",
    "nb_execution_allow_errors",
    "nb_execution_allow_errors",
    "nb_execution_timeout",
    "nb_execution_timeout",
    "project",
    "project_copyright",
    "release",
    "todo_include_todos",
    "version",
]
