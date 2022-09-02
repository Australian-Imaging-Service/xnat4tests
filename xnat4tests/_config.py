import json
from pathlib import Path

ROOT_DIR = Path.home() / ".xnat4tests"
config_json_path = ROOT_DIR / "config.json"


config = {
    "src_dir": Path(__file__).parent / "docker-src",
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
    "registry_port": "80",  # Must be 80 to avoid bug in XNAT CS config,
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
    "XNAT_VER": "1.8.4",
    "XNAT_CS_PLUGIN_VER": "3.1.1",
    "XNAT_BATCH_LAUNCH_PLUGIN_VER": "0.6.0",
    "JAVA_MS": "256m",
    "JAVA_MX": "2g"
}

# Load custom config saved in "config.json" and override defaults
if config_json_path.exists():
    with open(config_json_path) as f:
        custom_config = json.load(f)

    config.update((k, v) for k, v in custom_config.items() if k != 'build_args')
    if "build_args" in custom_config:
        config["build_args"].update(custom_config["build_args"])
