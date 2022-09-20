import logging
import click
from .launch import launch_xnat, launch_docker_registry, stop_xnat, stop_docker_registry

logger = logging.getLogger("xnat4tests")


@click.command()
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(
        [
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
        ]
    ),
    default="info",
    help="Set the level of logging detail",
)
def launch_cli(loglevel):

    set_loggers(loglevel)

    launch_xnat()


@click.command()
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(
        [
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
        ]
    ),
    default="info",
    help="Set the level of logging detail",
)
def stop_cli(loglevel):

    set_loggers(loglevel)

    stop_registry()
    stop_xnat()


@click.command()
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(
        [
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
        ]
    ),
    default="info",
    help="Set the level of logging detail",
)
def launch_registry(loglevel):

    set_loggers(loglevel)

    launch_docker_registry()


@click.command()
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(
        [
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
        ]
    ),
    default="info",
    help="Set the level of logging detail",
)
def stop_registry(loglevel):

    set_loggers(loglevel)

    stop_docker_registry()


def set_loggers(loglevel):

    logger.setLevel(loglevel.upper())
    ch = logging.StreamHandler()
    ch.setLevel(loglevel.upper())
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)
