
from . import _version
from .base import (
    start, start_registry, stop_xnat, stop_registry,
    connect)
from .utils import set_loggers
from .config import load_config


__version__ = _version.get_versions()['version']
