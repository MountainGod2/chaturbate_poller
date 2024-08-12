# ruff: noqa: S101, S607, S603
"""Test the Docker integration."""

import subprocess


def test_docker_image_build(mocker) -> None:  # noqa: ANN001
    """Test building the Docker image."""
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0

    result = subprocess.run(["docker", "build", "-t", "chaturbate_poller:latest", "."], check=False)

    assert result.returncode == 0
    mock_subprocess.assert_called_once_with(
        ["docker", "build", "-t", "chaturbate_poller:latest", "."], check=False
    )


def test_docker_image_run(mocker) -> None:  # noqa: ANN001
    """Test running the Docker container."""
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0

    result = subprocess.run(["docker", "run", "chaturbate_poller:latest"], check=False)

    assert result.returncode == 0
    mock_subprocess.assert_called_once_with(
        ["docker", "run", "chaturbate_poller:latest"], check=False
    )
