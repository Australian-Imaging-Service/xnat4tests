import os
import logging
from pathlib import Path


logger = logging.getLogger("xnat4tests")

try:
    XNAT4TESTS_HOME = Path(os.environ["XNAT4TESTS_HOME"])
except KeyError:
    XNAT4TESTS_HOME = Path.home() / ".xnat4tests"


def set_loggers(loglevel):

    logger.setLevel(loglevel.upper())
    ch = logging.StreamHandler()
    ch.setLevel(loglevel.upper())
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)
