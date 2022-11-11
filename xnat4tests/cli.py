import click
from .base import start_xnat, stop_xnat, restart_xnat
from .data import add_data, AVAILABLE_DATASETS
from .registry import start_registry, stop_registry
from .utils import set_loggers
from ._version import get_versions


LOGLEVEL_CHOICE = click.Choice(
    [
        "critical",
        "fatal",
        "error",
        "warning",
        "warn",
        "info",
        "debug",
    ]
)


@click.group(
    help="""Control the launch and configuration of an XNAT instance running inside a
single Docker container to be used for testing purposes"""
)
@click.option(
    "--config",
    "-c",
    type=str,
    default="default",
    help="The configuration YAML to use to launch the test instance",
)
@click.version_option(get_versions()["version"])
@click.pass_context
def cli(ctx, config):
    ctx.obj = config


@cli.command(
    name="start",
    help="Starts the test XNAT instance as specified by the configuration file",
)
@click.option(
    "--with-data",
    "-d",
    type=click.Choice(AVAILABLE_DATASETS),
    multiple=True,
    default=(),
    help=("Adds sample data into the newly created XNAT instance"),
)
@click.option(
    "--keep-mounts/--wipe-mounts",
    "-k/-w",
    type=bool,
    default=False,
    help=(
        "Whether to wipe the externally mounted directories (if present) before "
        "starting the container. Required if the 'archive' directory is externally "
        "mounted otherwise it won't match the Postgres DB, which is recreated for each "
        "instance of the container"
    ),
)
@click.option(
    "--rebuild/--reuse-build",
    type=bool,
    default=True,
    help=(
        "Rebuild the Docker image to pick up any configuration changes since it was "
        "built"
    ),
)
@click.option(
    "--relaunch/--reuse-launch",
    type=bool,
    default=False,
    help=(
        "Relaunch the Docker container instead of using an previously launched "
        "container if present"
    ),
)
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def start_cli(ctx, loglevel, keep_mounts, rebuild, relaunch, with_data):

    set_loggers(loglevel)

    start_xnat(
        config_name=ctx.obj, keep_mounts=keep_mounts, rebuild=rebuild, relaunch=relaunch
    )

    for dataset in with_data:
        add_data(dataset, config_name=ctx.obj)


@cli.command(
    name="stop", help="Stops the test XNAT instance named by the configuration file"
)
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def stop_cli(ctx, loglevel):

    set_loggers(loglevel)

    stop_registry(config_name=ctx.obj)
    stop_xnat(config_name=ctx.obj)


@cli.command(
    name="restart",
    help="Restarts the test XNAT instance as specified by the configuration file",
)
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def restart_cli(ctx, loglevel):

    set_loggers(loglevel)

    stop_registry(config_name=ctx.obj)
    restart_xnat(config_name=ctx.obj)


@cli.command(
    name="add-data",
    help="""Adds sample data to the XNAT instance

DATASET is the name of the dataset to add (out of ['dummydicom'])""",
)
@click.argument("dataset", type=click.Choice(AVAILABLE_DATASETS))
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def add_data_cli(ctx, loglevel, dataset):

    set_loggers(loglevel)
    add_data(dataset, config_name=ctx.obj)


@cli.group(
    help="""Launch/stop a local Docker image registry to test automatic pulling of
Docker images into XNAT's Container Service"""
)
def registry():
    pass


@registry.command(
    name="start",
    help="""Starts a Docker registry to connect to the XNAT instance as specified
in the configuration file""",
)
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def start_registry_cli(ctx, loglevel):

    set_loggers(loglevel)

    start_xnat(config_name=ctx.obj)  # Ensure XNAT has been started first
    start_registry(config_name=ctx.obj)


@registry.command(
    name="stop", help="Stops the Docker registry specified in the configuration file"
)
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def stop_registry_cli(ctx, loglevel):

    set_loggers(loglevel)

    stop_registry(config_name=ctx.obj)
