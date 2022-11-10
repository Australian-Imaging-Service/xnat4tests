from .base import start_xnat, stop_xnat, restart_xnat, connect
from .registry import start_registry, stop_registry, restart_registry
from . import _version


__version__ = _version.get_versions()["version"]
