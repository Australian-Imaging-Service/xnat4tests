import os
import yaml
import warnings
from pathlib import Path

try:
    XNAT4TESTS_HOME = Path(os.environ['XNAT4TESTS_HOME'])
except KeyError:
    XNAT4TESTS_HOME = Path.home() / ".xnat4tests"
config_file_path = XNAT4TESTS_HOME / "config.yaml"

XNAT4TESTS_HOME.mkdir(exist_ok=True)

config = {
    "xnat_root_dir": XNAT4TESTS_HOME / "xnat_root",
    "xnat_mnt_dirs": ["home/logs", "home/work", "build", "archive", "prearchive"],
    "docker_build_dir": XNAT4TESTS_HOME / "build",
    "docker_image": "xnat4tests",
    "docker_container": "xnat4tests",
    "docker_host": "localhost",
    # This shouldn't be changed as it needs to be the same as the internal for the
    # container service to work
    "xnat_port": "8080",
    "docker_registry_image": "registry",
    "docker_registry_container": "xnat4tests-docker-registry",
    "docker_network_name": "xnat4tests",
    # Must be 80 to avoid bug in XNAT CS config,
    "registry_port": "80",
    "xnat_user": "admin",
    "xnat_password": "admin",
    "connection_attempts": 20,
    "connection_attempt_sleep": 5,
}


# XNAT build args
config["build_args"] = {
    "XNAT_VER": "1.8.5",
    "XNAT_CS_PLUGIN_VER": "3.2.0",
    "XNAT_BATCH_LAUNCH_PLUGIN_VER": "0.6.0",
    "JAVA_MS": "256m",
    "JAVA_MX": "2g"
}

# Load custom config saved in "config.json" and override defaults
if config_file_path.exists():
    with open(config_file_path) as f:
        custom_config = yaml.load(f, Loader=yaml.Loader)

    config.update((k, v) for k, v in custom_config.items() if k != 'build_args')
    if "build_args" in custom_config:
        config["build_args"].update(custom_config["build_args"])

    if str(config["xnat_port"]) != "8080":
        warnings.warn(
            f"Changing XNAT port from 8080 to {config['xnat_port']} will cause "
            "the container service plugin not to work")

    if str(config["registry_port"]) != "80":
        warnings.warn(
            f"Changing XNAT registry port from 80 to {config['registry_port']} is "
            "currently not compatible with the XNAT container service image pull "
            "feature")

    config["docker_build_dir"] = Path(config["docker_build_dir"])
    if not config["docker_build_dir"].parent.exists():
        raise Exception(
            f"Parent of build directory {str(config['docker_build_dir'].parent)} "
            "does not exist")

    config["xnat_root_dir"] = Path(config["xnat_root_dir"])
    if not config["xnat_root_dir"].parent.exists():
        raise Exception(
            f"Parent of XNAT root directory {str(config['xnat_root_dir'].parent)} does not exist")
