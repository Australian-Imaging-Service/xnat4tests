import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import yaml
import pytest

tmp_home_dir = tempfile.mkdtemp()
with patch.dict(os.environ, {"XNAT4TESTS_HOME": tmp_home_dir}):
    with open(Path(tmp_home_dir) / "config.yaml", "w") as f:
        yaml.dump(
            {
                "docker_image": "xnat4tests_unittest",
                "docker_container": "xnat4tests_unittest",
                "xnat_port": "8090",
                "registry_port": "5555",
                "xnat_root_dir": os.path.join(tmp_home_dir, "xnat_root_changed"),
                "build_args": {"JAVA_MX": "1g"},
            },
            f,
        )
    from xnat4tests import config, launch_xnat, stop_xnat, connect


@pytest.fixture(scope="session")
def home_dir():  # Makes the home dir show up on test output
    return tmp_home_dir


@pytest.fixture(scope="session")
def login():
    launch_xnat()
    yield connect()
    stop_xnat()


def test_config(home_dir):

    assert config["xnat_root_dir"] == Path(home_dir) / "xnat_root_changed"
    assert config["xnat_root_dir"].exists()
    assert config["docker_image"] == "xnat4tests_unittest"
    assert config["docker_container"] == "xnat4tests_unittest"
    assert config["xnat_port"] == "8090"
    assert config["registry_port"] == "5555"
    assert config["build_args"] == {"JAVA_MX": "1g"}


def test_launch(login):

    PROJECT = "MY_TEST_PROJECT"
    SUBJECT = "MY_TEST_SUBJECT"
    SESSION = "MY_TEST_SESSION"

    # Create project
    login.put(f"/data/archive/projects/{PROJECT}")

    # Create subject
    xsubject = login.classes.SubjectData(label=SUBJECT, parent=login.projects[PROJECT])
    # Create session
    xsession = login.classes.MrSessionData(label=SESSION, parent=xsubject)

    temp_dir = Path(tempfile.mkdtemp())
    a_file = temp_dir / "a_file.txt"
    with open(a_file, "w") as f:
        f.write("a file")

    xresource = login.classes.ResourceCatalog(
        parent=xsession, label="A_RESOURCE", format="text"
    )
    xresource.upload(str(a_file), "a_file")

    assert [p.name for p in (config["xnat_root_dir"] / "archive").iterdir()] == [
        PROJECT
    ]
    assert [
        p.name
        for p in (config["xnat_root_dir"] / "archive" / PROJECT / "arc001").iterdir()
    ] == [SESSION]
