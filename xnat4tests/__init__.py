from .base import start_xnat, stop_xnat, restart_xnat, connect
from .registry import start_registry, stop_registry
from .data import add_data
from .config import Config
from . import _version


__version__ = _version.get_versions()["version"]
