from ._config import config
from .launch import (
    launch_xnat, launch_docker_registry, stop_xnat, stop_docker_registry,
    connect, set_loggers)

from . import _version
__version__ = _version.get_versions()['version']
