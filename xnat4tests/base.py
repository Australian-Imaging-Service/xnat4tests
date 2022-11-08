import stat
import shutil
import time
import requests
from pathlib import Path
import attrs
import docker
from .utils import logger
import xnat
from .config import Config


SRC_DIR = Path(__file__).parent / "docker-src"


def start_xnat(config_name="default", keep_mounts=False, rebuild=True, relaunch=False):
    """Starts an XNAT repository within a single Docker container that has
    has the container service plugin configured to access the Docker socket
    to launch sibling containers.

    Directories listed in "xnat_mnt_dirs" are mounted from the host machine at
    "xnat_root" for convenience and to facilitate methods that mock the
    environment containers run in within the XNAT container service.

    Parameters
    ----------
    config : Config or str
        Either the configuration dictionary or the name of the configuration file to
        load it from, that specifies the launch parameters of the test container.
        With the exception of the "default" configuration, there should be a configuration
        file at $XNAT4TESTS_HOME/config/<config-name>.yaml (where XNAT4TESTS_HOME is
        $HOME/.xnat4tests by default)
    keep_mounts : bool
        Whether to wipe out the mount directories before rebooting. Required if mounting
        in the archive directory as otherwise it won't match up with the Postgres DB
        within the container
    rebuild : bool
        rebuild the Docker image whether a matching image exists or not
    relaunch : bool
        relaunch the container whether a matching container exists or not
    """

    config = Config.load(config_name)

    dc = docker.from_env()

    if rebuild:
        if config.docker_build_dir.exists():
            shutil.rmtree(config.docker_build_dir)
        logger.info(
            "Building %s in '%s' directory",
            config.docker_image,
            str(config.docker_build_dir),
        )
        shutil.copytree(SRC_DIR, config.docker_build_dir)
        try:
            image, _ = dc.images.build(
                path=str(config.docker_build_dir),
                tag=config.docker_image,
                buildargs={k.upper(): v for k, v in attrs.asdict(config.build_args).items()},
            )
        except docker.errors.BuildError as e:
            build_log = "\n".join(ln.get("stream", "") for ln in e.build_log)
            raise RuntimeError(
                f"Building '{config.docker_image}' in '{str(config.docker_build_dir)}' "
                f"failed with the following errors:\n\n{build_log}"
            )
        logger.info("Built %s successfully", config.docker_image)
    else:
        try:
            image = dc.images.get(config.docker_image)
        except docker.errors.ImageNotFound:
            rebuild = True

    try:
        container = dc.containers.get(config.docker_container)
    except docker.errors.NotFound:
        relaunch = True
    else:
        if relaunch or container.image != image:
            logger.info("Stopping existing %s container", config.docker_container)
            container.stop()
            while config.docker_container in (c.name for c in dc.containers.list()):
                logger.info("Waiting for %s container to be autoremoved",
                            config.docker_container)
            relaunch = True

    if relaunch:
        logger.info(
            "Did not find %s container, relaunching", config.docker_container
        )
        volumes = {
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}
        }
        # Mount in the XNAT root directory for debugging and to allow access
        # from the Docker host when using the container service

        # Clear previous ROOT directories
        if not keep_mounts:
            try:
                shutil.rmtree(config.xnat_root_dir)
            except FileNotFoundError:
                pass
        for dname in config.xnat_mnt_dirs:
            dpath = config.xnat_root_dir / dname
            dpath.mkdir(parents=True, exist_ok=True)
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
            ports={"8080/tcp": config.xnat_port},
            remove=True,
            name=config.docker_container,
            # Expose the XNAT archive dir outside of the XNAT docker container
            # to simulate what the XNAT container service exposes to running
            # pipelines, and the Docker socket for the container service to
            # to use
            network=docker_network().id,
            volumes=volumes,
        )
        logger.info("%s launched successfully", config.docker_container)
    else:
        logger.info("Found existing %s container, reusing", config.docker_container)

    # Need to give time for XNAT to get itself ready after it has
    # started so we try multiple times until giving up trying to connect
    logger.info("Attempting to connect to %s", config.xnat_uri)
    for attempts in range(1, config.connection_attempts + 1):
        try:
            login = connect(config)
        except (xnat.exceptions.XNATError, requests.ConnectionError):
            if attempts == config.connection_attempts:
                raise
            else:
                logger.debug(
                    "Attempt %d/%d to connect to %s failed, retrying",
                    attempts,
                    config.connection_attempts,
                    config.xnat_uri,
                )
                time.sleep(config.connection_attempt_sleep)
        else:
            break
    logger.info("Connected to %s successfully", config.xnat_uri)

    if relaunch:
        # Set the path translations to point to the mounted XNAT home directory
        with login:
            if "containers" in login.get("/xapi/plugins").json():
                logger.info("Configuing docker server for container service")
                login.post(
                    "/xapi/docker/server",
                    json={
                        # 'id': 2,
                        "name": "Local socket",
                        "host": "unix:///var/run/docker.sock",
                        "cert-path": "",
                        "swarm-mode": False,
                        "path-translation-xnat-prefix": "/data/xnat",
                        "path-translation-docker-prefix": str(config.xnat_root_dir),
                        "pull-images-on-xnat-init": False,
                        "container-user": "",
                        "auto-cleanup": True,
                        "swarm-constraints": [],
                        "ping": True,
                    },
                )

    return container


def stop_xnat(config_name="default"):

    config = Config.load(config_name)

    dc = docker.from_env()
    try:
        container = dc.containers.get(config.docker_container)
    except docker.errors.NotFound:
        logger.info("Test XNAT was not running at %s", config.docker_container)
    else:
        logger.info("Stopping test XNAT running at %s", config.docker_container)
        container.stop()


def restart_xnat(config_name="default"):

    config = Config.load(config_name)

    dc = docker.from_env()
    try:
        container = dc.containers.get(config.docker_container)
    except docker.errors.NotFound:
        raise Exception("Test XNAT was not running at %s", config.docker_container)
    container.restart()


def docker_network(config_name="default"):

    config = Config.load(config_name)

    dc = docker.from_env()
    try:
        network = dc.networks.get(config.docker_network_name)
    except docker.errors.NotFound:
        network = dc.networks.create(config.docker_network_name)
    return network


def connect(config_name="default"):

    config = Config.load(config_name)

    logger.info("Connecting to %s as '%s'", config.xnat_uri, "admin")
    return xnat.connect(config.xnat_uri, user="admin", password="admin")
