import os
import logging
from pathlib import Path

logger = logging.getLogger("xnat4tests")

try:
    XNAT4TESTS_HOME = Path(os.environ['XNAT4TESTS_HOME'])
except KeyError:
    XNAT4TESTS_HOME = Path.home() / ".xnat4tests"

XNAT4TESTS_HOME.mkdir(exist_ok=True)
