# ruff: noqa: S101
"""Tests for the config module."""

from chaturbate_poller.config import load_config_from_file, load_env_variables


def test_load_config_from_file(tmp_path) -> None:  # noqa: ANN001
    """Test the load_config_from_file function."""
    config_content = """
    username: "test_user"
    token: "test_token"
    use_database: true
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    config = load_config_from_file(config_file)

    assert config["username"] == "test_user"
    assert config["token"] == "test_token"  # noqa: S105
    assert config["use_database"] is True


def test_load_env_variables(monkeypatch) -> None:  # noqa: ANN001
    """Test the load_env_variables function."""
    monkeypatch.setenv("CB_USERNAME", "test_user")
    monkeypatch.setenv("CB_TOKEN", "test_token")
    monkeypatch.setenv("USE_DATABASE", "true")

    config = load_env_variables()

    assert config["username"] == "test_user"
    assert config["token"] == "test_token"  # noqa: S105
    assert config["use_database"] is True
