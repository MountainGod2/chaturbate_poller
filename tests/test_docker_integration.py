# ruff: noqa: S101, S603
"""Test the Docker integration."""

import shutil
import subprocess


def test_docker_build_and_run(mocker) -> None:  # noqa: ANN001
    """Test the full Docker build and run process."""
    docker_executable = shutil.which("docker")
    assert docker_executable is not None, "Docker is not installed."

    # Mock subprocess for Docker build
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=["docker", "build"], returncode=0),
    )
    subprocess.run([docker_executable, "build", "-t", "chaturbate_poller:latest", "."], check=True)

    # Mock subprocess for Docker run
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=["docker", "run"], returncode=0),
    )
    subprocess.run([docker_executable, "run", "chaturbate_poller:latest"], check=True)

    assert True
