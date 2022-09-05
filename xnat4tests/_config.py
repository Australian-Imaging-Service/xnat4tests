import yaml
import warnings
from pathlib import Path

ROOT_DIR = Path.home() / ".xnat4tests"
config_file_path = ROOT_DIR / "config.yaml"


config = {
    "build_dir": ROOT_DIR / "build",
    "xnat_root_dir": ROOT_DIR / "xnat_root",
    "xnat_mnt_dirs": ["home/logs", "home/work", "build", "archive", "prearchive"],
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

config.update({
    "xnat_uri": f"http://{config['docker_host']}:{config['xnat_port']}",
    "registry_uri": f"{config['docker_host']}"  # :{REGISTRY_PORT}',
})

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
