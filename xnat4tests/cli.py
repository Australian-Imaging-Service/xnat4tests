import click
from .base import start_xnat, stop_xnat, restart_xnat
from .registry import start_registry, stop_registry, restart_registry
from .utils import set_loggers


@click.group()
@click.option(
    "--config",
    "-c",
    type=str,
    default="default",
    help="The configuration YAML to use to launch the test instance",
)
@click.pass_context
def cli(ctx, config):
    ctx.obj = config


@cli.command(name="start")
@click.option(
    "--wipe-mounts/--keep-mounts",
    "-w/-k",
    type=bool,
    help=(
        "Whether to wipe the externally mounted directories (if present) before "
        "starting the container. Requred if the 'archive' directory is externally "
        "mounted otherwise it won't match the Postgres DB, which is recreated for each "
        "instance of the container"
    )
)
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
@click.pass_context
def start_cli(ctx, loglevel, wipe_mounts):

    set_loggers(loglevel)

    start_xnat(config=ctx.obj)


@cli.command(name="stop")
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
@click.pass_context
def stop_cli(ctx, loglevel):

    set_loggers(loglevel)

    stop_registry(config=ctx.obj)
    stop_xnat(config=ctx.obj)


@cli.group()
def registry():
    pass


@registry.command(name="start")
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
@click.pass_context
def start_registry_cli(ctx, loglevel):

    set_loggers(loglevel)

    start_xnat(config=ctx.obj)  # Ensure XNAT has been started first
    start_registry(config=ctx.obj)


@registry.command(name="stop")
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
@click.pass_context
def stop_registry_cli(ctx, loglevel):

    set_loggers(loglevel)

    stop_registry(config=ctx.obj)
