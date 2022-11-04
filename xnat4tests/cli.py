import click
from .launch import launch_xnat, launch_docker_registry, stop_xnat, stop_docker_registry
from .utils import set_loggers


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

    launch_xnat()
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
