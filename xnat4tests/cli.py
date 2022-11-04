import click
from .base import start, start_registry, stop_xnat, stop_registry
from .utils import set_loggers


@click.group()
@click.option(
    "--config",
    "-c",
    type=str,
    default="default",
    help="The configuration YAML to use to launch the test instance"
)
def cli():
    pass


@cli.command()
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
def start_cli(loglevel):

    set_loggers(loglevel)

    start()


@cli.command()
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


@cli.group()
def registry():
    pass


@registry.command()
@click.option(
    "start",
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
def start_registry_cli(loglevel):

    set_loggers(loglevel)

    start()
    start_registry()


@registry.command()
@click.option(
    "stop",
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
def stop_registry_cli(loglevel):

    set_loggers(loglevel)

    stop_registry()
