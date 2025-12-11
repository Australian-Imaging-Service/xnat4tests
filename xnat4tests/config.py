import yaml
import warnings
from pathlib import Path
import typing as ty
import attrs
from .utils import XNAT4TESTS_HOME


DEFAULT_XNAT_ROOT = XNAT4TESTS_HOME / "xnat_root" / "default"
DEFAULT_BUILD_DIR = XNAT4TESTS_HOME / "build"


@attrs.define
class BuildArgs:
    xnat_version: str = "1.9.3"
    xnat_cs_plugin_version: str = "3.7.3"
    xnat_batch_launch_plugin_version: str = "0.9.0-xpl"
    java_ms: str = "256m"
    java_mx: str = "2g"


@attrs.define
class Config:
    xnat_root_dir: Path = attrs.field(default=DEFAULT_XNAT_ROOT, converter=Path)
    xnat_mnt_dirs: ty.List[str] = [
        "home/logs",
        "home/work",
        "build",
        "archive",
        "prearchive",
    ]
    docker_build_dir: Path = attrs.field(default=DEFAULT_BUILD_DIR, converter=Path)
    docker_image: str = "xnat4tests"
    docker_container: str = "xnat4tests"
    docker_host: str = "localhost"
    # This shouldn't be changed as it needs to be the same as the internal for the
    # container service to work
    xnat_port: str = attrs.field(default="8080")
    docker_registry_image: str = "registry"
    docker_registry_container: str = "xnat4tests-docker-registry"
    docker_network_name: str = "xnat4tests"
    # Must be 80 to use as XNAT registry avoid bug in XNAT CS config
    registry_port: str = attrs.field(default="80")
    # xnat_user: str = "admin"
    # xnat_password: str = "admin"
    connection_attempts: int = 20
    connection_attempt_sleep: int = 5
    build_args: BuildArgs = attrs.field(
        factory=dict, converter=lambda d: BuildArgs(**d)
    )
    loaded_from: ty.Optional[Path] = None

    # These are fixed at the defaults for now. In future we might want to
    # have these set in the configuration
    xnat_user = "admin"
    xnat_password = "admin"

    @xnat_port.validator
    def xnat_port_validator(self, _, xnat_port):
        if xnat_port != "8080":
            warnings.warn(
                f"Changing XNAT port from 8080 to {xnat_port} will cause "
                "the container service plugin not to work"
            )

    @registry_port.validator
    def registry_port_validator(self, _, registry_port):
        if registry_port != "80":
            warnings.warn(
                f"Changing XNAT registry port from 80 to {registry_port} is "
                "currently not compatible with the XNAT container service image pull "
                "feature"
            )

    @docker_build_dir.validator
    def docker_build_dir_validator(self, _, docker_build_dir):
        if (
            docker_build_dir != DEFAULT_BUILD_DIR
            and not docker_build_dir.parent.exists()
        ):
            raise Exception(
                f"Parent of build directory {str(docker_build_dir.parent)} "
                "does not exist"
            )

    @xnat_root_dir.validator
    def xnat_root_dir_validator(self, _, xnat_root_dir):
        if xnat_root_dir != DEFAULT_XNAT_ROOT and not xnat_root_dir.parent.exists():
            raise Exception(
                f"Parent of XNAT root directory {str(xnat_root_dir.parent)} does not "
                "exist"
            )

    @classmethod
    def load(cls, name):
        """Loads a configuration object from a YAML file

        Parameters
        ----------
        name : str or Path or Config
            the name or path of the configuration file to load

        Returns
        -------
        Config
            the loaded configuration

        Raises
        ------
        Exception
            if the provided "name" contains a path separator and does not match a path
            to an existing file
        KeyError
            if the provided name does not match an existing file
        """
        if isinstance(name, Config):
            return name  # preloaded configuration
        elif (
            isinstance(name, Path) or "/" in name or "\\" in name
        ):  # Treat as file path instead of name
            config_file_path = Path(name)
            if not config_file_path.exists():
                raise Exception(
                    "Did not find configuration file at explicit path "
                    f"'{str(config_file_path)}"
                )
        else:  # Treat as the filename base of a YAML file in the within xnat4tests HOME
            config_file_path = XNAT4TESTS_HOME / "configs" / f"{name}.yaml"

            # Create parent dir if it doesn't already exist
            config_file_path.parent.mkdir(exist_ok=True, parents=True)

        # Load custom config saved in "config.json" and override defaults
        if not config_file_path.exists():
            if name == "default":
                # Write a default configuration file with all options commented out for ease
                # of customisation
                yaml_lines = yaml.dump(attrs.asdict(Config())).split("\n")
                with open(config_file_path, "w") as f:
                    for line in yaml_lines:
                        f.write("#" + line + "\n")
            else:
                raise KeyError(
                    f"Could not find configuration file at {config_file_path}"
                )

        with open(config_file_path) as f:
            dct = yaml.load(f, Loader=yaml.Loader)

        if dct is None:
            dct = {}

        return cls(loaded_from=config_file_path, **dct)

    @property
    def xnat_uri(self):
        return f"http://{self.docker_host}:{self.xnat_port}"

    @property
    def registry_uri(self):
        return self.docker_host
