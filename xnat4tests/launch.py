import stat
import shutil
import time
import requests
from pathlib import Path
import logging
import docker
import click
import xnat
from ._config import config


logger = logging.getLogger("xnat4tests")


SRC_DIR = Path(__file__).parent / "docker-src"

xnat_uri = f"http://{config['docker_host']}:{config['xnat_port']}"
registry_uri = f"{config['docker_host']}"


def launch_xnat():
    """Starts an XNAT repository within a single Docker container that has
    has the container service plugin configured to access the Docker socket
    to launch sibling containers.

    The archive, prearchive, build, logs and work directories are mounted from
    the host machine at `xnat4tests.config["xnat_root"]`
    for convenience and to facilitate methods that mock the
    environment containers run in within the XNAT container service.
    """

    dc = docker.from_env()

    try:
        image = dc.images.get(config["docker_image"])
    except docker.errors.ImageNotFound:
        logger.info(
            "Building %s in '%s' directory",
            config["docker_image"],
            str(config["docker_build_dir"]),
        )
        shutil.rmtree(config["docker_build_dir"], ignore_errors=True)
        shutil.copytree(SRC_DIR, config["docker_build_dir"])
        try:
            image, _ = dc.images.build(
                path=str(config["docker_build_dir"]),
                tag=config["docker_image"],
                buildargs=config["build_args"],
            )
        except docker.errors.BuildError as e:
            build_log = "\n".join(ln.get("stream", "") for ln in e.build_log)
            raise RuntimeError(
                f"Building '{config['docker_image']}' in '{str(config['docker_build_dir'])}' "
                f"failed with the following errors:\n\n{build_log}"
            )
        logger.info("Built %s successfully", config["docker_image"])

    try:
        container = dc.containers.get(config["docker_container"])
    except docker.errors.NotFound:
        logger.info(
            "Did not find %s container, relaunching", config["docker_container"]
        )
        volumes = {
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}
        }
        # Mount in the XNAT root directory for debugging and to allow access
        # from the Docker host when using the container service
        # Clear previous ROOT directories
        shutil.rmtree(config["xnat_root_dir"], ignore_errors=True)
        for dname in config["xnat_mnt_dirs"]:
            dpath = config["xnat_root_dir"] / dname
            dpath.mkdir(parents=True)
            # Set set-group-ID bit so sub-directories (created by root in
            # Docker inherit GID of launching user)
            dpath.chmod(
                stat.S_IRUSR
                | stat.S_IWUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IWGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH
                | stat.S_ISGID
            )
            volumes[str(dpath)] = {"bind": "/data/xnat/" + dname, "mode": "rw"}

        container = dc.containers.run(
            image.tags[0],
            detach=True,
            ports={"8080/tcp": config["xnat_port"]},
            remove=True,
            name=config["docker_container"],
            # Expose the XNAT archive dir outside of the XNAT docker container
            # to simulate what the XNAT container service exposes to running
            # pipelines, and the Docker socket for the container service to
            # to use
            network=docker_network().id,
            volumes=volumes,
        )
        logger.info("%s launched successfully", config["docker_container"])

    # Need to give time for XNAT to get itself ready after it has
    # started so we try multiple times until giving up trying to connect
    logger.info("Attempting to connect to %s", xnat_uri)
    for attempts in range(1, config["connection_attempts"] + 1):
        try:
            login = connect()
        except (xnat.exceptions.XNATError, requests.ConnectionError):
            if attempts == config["connection_attempts"]:
                raise
            else:
                logger.debug(
                    "Attempt %d/%d to connect to %s failed, retrying",
                    config["connection_attempts"],
                    config["connection_attempt_sleep"],
                    xnat_uri,
                )
                time.sleep(config["connection_attempt_sleep"])
        else:
            break

    # Set the path translations to point to the mounted XNAT home directory
    logger.info("Configuing docker server for container service")
    with login:
        login.post(
            "/xapi/docker/server",
            json={
                # 'id': 2,
                "name": "Local socket",
                "host": "unix:///var/run/docker.sock",
                "cert-path": "",
                "swarm-mode": False,
                "path-translation-xnat-prefix": "/data/xnat",
                "path-translation-docker-prefix": str(config["xnat_root_dir"]),
                "pull-images-on-xnat-init": False,
                "container-user": "",
                "auto-cleanup": True,
                "swarm-constraints": [],
                "ping": True,
            },
        )

        # Set registry URI, Not working due to limitations in XNAT UI
        # login.post('/xapi/docker/hubs/1', json={
        #     "name": "testregistry",
        #     "url": f"https://host.docker.internal"})

    return container


def launch_docker_registry():
    xnat_docker_network = docker_network()
    dc = docker.from_env()
    try:
        image = dc.images.get(config["docker_registry_image"])
    except docker.errors.ImageNotFound:
        logger.info(f"Pulling {config['docker_registry_image']}")
        image = dc.images.pull(config["docker_registry_image"])

    try:
        container = dc.containers.get(config["docker_registry_container"])
    except docker.errors.NotFound:
        container = dc.containers.run(
            image.tags[0],
            detach=True,
            ports={"5000/tcp": config["registry_port"]},
            network=xnat_docker_network.id,
            remove=True,
            name=config["docker_registry_container"],
        )

    return container


def stop_xnat():
    dc = docker.from_env()
    try:
        container = dc.containers.get(config["docker_container"])
    except docker.errors.NotFound:
        logger.info("Test XNAT was not running at %s", config["docker_container"])
    else:
        logger.info("Stopping test XNAT running at %s", config["docker_container"])
        container.stop()


def stop_docker_registry():
    launch_docker_registry().stop(config["docker_registry_container"])


def docker_network():
    dc = docker.from_env()
    try:
        network = dc.networks.get(config["docker_network_name"])
    except docker.errors.NotFound:
        network = dc.networks.create(config["docker_network_name"])
    return network


def connect():
    logger.info("Connecting to %s as '%s'", xnat_uri, config["xnat_user"])
    return xnat.connect(
        xnat_uri, user=config["xnat_user"], password=config["xnat_password"]
    )


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
    help="Set the level of logging detail",
)
def cli(loglevel):

    set_loggers(loglevel)

    launch_xnat()


def set_loggers(loglevel):

    logger.setLevel(loglevel.upper())
    ch = logging.StreamHandler()
    ch.setLevel(loglevel.upper())
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)
