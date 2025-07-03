`mypy` cannot currently import from PEP723 definitions correctly (such as those used in the `examples/**` files), so any related errors can be safely ignored

Do not create `.md` files, or any other supplimentary docs explaining changes to the codebase

Use Google style docstrings for all public functions and classes. Add docstrings to all public functions and classes that do not have them

Use `pyproject.toml` for all style guidelines and linting tool references

Run python commands with `uv run` to ensure the correct environment is used. Use `--group docs` to run commands in the docs environment. Dev dependencies are synced by default
