import stat
import shutil
import time
import requests
import docker
import xnat
from ._config import config


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
        shutil.rmtree(config["build_dir"], ignore_errors=True)
        shutil.copytree(config["src_dir"], config["build_dir"])
        image, _ = dc.images.build(
            path=str(config["build_dir"]),
            tag=config["docker_image"],
            buildargs=config['build_args'])

    try:
        container = dc.containers.get(config["docker_container"])
    except docker.errors.NotFound:
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

    # Need to give time for XNAT to get itself ready after it has
    # started so we try multiple times until giving up trying to connect
    for attempts in range(1, config["connection_attempts"] + 1):
        try:
            login = connect()
        except (xnat.exceptions.XNATError, requests.ConnectionError):
            if attempts == config["connection_attempts"]:
                raise
            else:
                time.sleep(config["connection_attempt_sleep"])
        else:
            break

    # Set the path translations to point to the mounted XNAT home directory
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

        # Set registry URI
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
    launch_xnat().stop()


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
    return xnat.connect(
        config["xnat_uri"], user=config["xnat_user"], password=config["xnat_password"]
    )
