from .config import config
from .launch import launch_xnat, stop_xnat, connect
from .registry import launch_docker_registry, stop_docker_registry
from .cli import set_loggers

from . import _version

__version__ = _version.get_versions()["version"]
