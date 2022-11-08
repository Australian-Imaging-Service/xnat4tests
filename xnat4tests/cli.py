import click
from .base import start_xnat, stop_xnat, restart_xnat
from .registry import start_registry, stop_registry, restart_registry
from .utils import set_loggers

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


@click.group
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
    "--keep-mounts/--wipe-mounts",
    "-k/-w",
    type=bool,
    default=False,
    help=(
        "Whether to wipe the externally mounted directories (if present) before "
        "starting the container. Requred if the 'archive' directory is externally "
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
def start_cli(ctx, loglevel, keep_mounts, rebuild, relaunch):

    set_loggers(loglevel)

    start_xnat(
        config_name=ctx.obj, keep_mounts=keep_mounts, rebuild=rebuild, relaunch=relaunch
    )


@cli.command(name="stop")
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


@cli.command(name="restart")
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


@cli.group
def registry():
    pass


@registry.command(name="start")
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


@registry.command(name="stop")
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


@registry.command(name="restart")
@click.option(
    "--loglevel",
    "-l",
    type=LOGLEVEL_CHOICE,
    default="info",
    help="Set the level of logging detail",
)
@click.pass_context
def restart_registry_cli(ctx, loglevel):

    set_loggers(loglevel)

    restart_registry(config_name=ctx.obj)
