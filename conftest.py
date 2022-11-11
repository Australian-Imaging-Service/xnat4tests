import os
import tempfile
import pytest
import docker
import yaml
from pathlib import Path
from click.testing import CliRunner
from xnat4tests.base import start_xnat, stop_xnat
from xnat4tests.config import Config
from xnat4tests.utils import set_loggers


set_loggers("debug")


@pytest.fixture()
def work_dir():  # Makes the home dir show up on test output
    return Path(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def home_dir():  # Makes the home dir show up on test output
    return Path(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def xnat_root_dir(home_dir):
    root_dir = home_dir / "xnat_root"
    root_dir.mkdir()
    return root_dir


@pytest.fixture(scope="session")
def config(home_dir, xnat_root_dir):

    config_path = home_dir / "test-config.yaml"
    root_dir = xnat_root_dir / "test-config"
    root_dir.mkdir()
    with open(config_path, "w") as f:
        yaml.dump(
            {
                "docker_image": "xnat4tests_unittest",
                "docker_container": "xnat4tests_unittest",
                "xnat_port": "8090",
                "registry_port": "5555",
                "xnat_root_dir": str(root_dir),
                "build_args": {"java_mx": "1g"},
            },
            f,
        )

    return Config.load(config_path)


@pytest.fixture(scope="session")
def launched_xnat(config):

    dc = docker.from_env()
    try:
        container = dc.containers.get(config.docker_container)
    except docker.errors.NotFound:
        pass
    else:
        container.stop()

    try:
        image = dc.images.get(config.docker_image)
    except docker.errors.ImageNotFound:
        pass
    else:
        dc.images.remove(image.id)

    yield start_xnat(config)
    stop_xnat(config)


# For debugging in IDE's don't catch raised exceptions and let the IDE
# break at it
if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value

    CATCH_CLI_EXCEPTIONS = False
else:
    CATCH_CLI_EXCEPTIONS = True


@pytest.fixture
def catch_cli_exceptions():
    return CATCH_CLI_EXCEPTIONS


@pytest.fixture
def cli_runner(catch_cli_exceptions):
    def invoke(*args, catch_exceptions=catch_cli_exceptions, **kwargs):
        runner = CliRunner()
        result = runner.invoke(*args, catch_exceptions=catch_exceptions, **kwargs)
        return result

    return invoke
