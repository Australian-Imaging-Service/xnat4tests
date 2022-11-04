
from . import _version
from .launch import (
    launch_xnat, launch_docker_registry, stop_xnat, stop_docker_registry,
    connect)
from .utils import set_loggers
from .config import load_config


__version__ = _version.get_versions()['version']
