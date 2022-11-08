from . import _version
from .base import start, stop_xnat, connect
from .utils import set_loggers
from .config import load_config


__version__ = _version.get_versions()["version"]
