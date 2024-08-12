# ruff: noqa: S101, S603
"""Test the Docker integration."""

import shutil
import subprocess


def test_docker_image_build(mocker) -> None:  # noqa: ANN001
    """Test building the Docker image."""
    docker_executable = shutil.which("docker")  # Find the full path of the Docker executable
    assert docker_executable is not None, "Docker is not installed or not found in PATH"

    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0

    result = subprocess.run(
        [docker_executable, "build", "-t", "chaturbate_poller:latest", "."], check=True
    )

    assert result.returncode == 0
    mock_subprocess.assert_called_once_with(
        [docker_executable, "build", "-t", "chaturbate_poller:latest", "."], check=True
    )


def test_docker_image_run(mocker) -> None:  # noqa: ANN001
    """Test running the Docker container."""
    docker_executable = shutil.which("docker")  # Find the full path of the Docker executable
    assert docker_executable is not None, "Docker is not installed or not found in PATH"

    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0

    result = subprocess.run([docker_executable, "run", "chaturbate_poller:latest"], check=True)

    assert result.returncode == 0
    mock_subprocess.assert_called_once_with(
        [docker_executable, "run", "chaturbate_poller:latest"], check=True
    )
