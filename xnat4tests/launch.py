import shutil
import time
import requests
import docker
import xnat


from .config import (
    SRC_DIR, BUILD_DIR, DOCKER_IMAGE, DOCKER_CONTAINER, XNAT_MNT_DIRS,
    XNAT_PORT, XNAT_ROOT_DIR,
    DOCKER_NETWORK_NAME, XNAT_URI, REGISTRY_PORT, XNAT_USER, XNAT_PASSWORD,
    DOCKER_REGISTRY_IMAGE, DOCKER_REGISTRY_CONTAINER, CONNECTION_ATTEMPTS,
    CONNECTION_ATTEMPT_SLEEP)


def launch_xnat():
    """Starts an XNAT repository within a single Docker container that has
    has the container service plugin configured to access the Docker socket
    to launch sibling containers.

    The archive, prearchive, build, logs and work directories are mounted from
    the host machine at `xnat4tests.config.XNAT_ROOT`
    for convenience and to facilitate methods that mock the
    environment containers run in within the XNAT container service.
    """

    dc = docker.from_env()

    try:
        image = dc.images.get(DOCKER_IMAGE)
    except docker.errors.ImageNotFound:
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        shutil.copytree(SRC_DIR, BUILD_DIR)
        image, _ = dc.images.build(path=str(BUILD_DIR), tag=DOCKER_IMAGE)
    
    try:
        container = dc.containers.get(DOCKER_CONTAINER)
    except docker.errors.NotFound:
        volumes = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock',
                                            'mode': 'rw'}}
        # Mount in the XNAT root directory for debugging and to allow access
        # from the Docker host when using the container service
        # Clear previous ROOT directories
        shutil.rmtree(XNAT_ROOT_DIR, ignore_errors=True)
        for  dname in XNAT_MNT_DIRS:
            dpath = XNAT_ROOT_DIR / dname
            dpath.mkdir(parents=True)
            volumes[str(dpath)] = {'bind': '/data/xnat/' + dname,
                                   'mode': 'rw'}

        container = dc.containers.run(
            image.tags[0], detach=True, ports={
                '8080/tcp': XNAT_PORT},
            remove=True, name=DOCKER_CONTAINER,
            # Expose the XNAT archive dir outside of the XNAT docker container
            # to simulate what the XNAT container service exposes to running
            # pipelines, and the Docker socket for the container service to
            # to use
            network=docker_network().id,
            volumes=volumes)


    # Need to give time for XNAT to get itself ready after it has
    # started so we try multiple times until giving up trying to connect
    for attempts in range(1, CONNECTION_ATTEMPTS + 1):
        try:
            login = connect()
        except (xnat.exceptions.XNATError, requests.ConnectionError):
            if attempts == CONNECTION_ATTEMPTS:
                raise
            else:
                time.sleep(CONNECTION_ATTEMPT_SLEEP)
        else:
            break

    # Set the path translations to point to the mounted XNAT home directory
    with login:
        login.post('/xapi/docker/server', json={
            # 'id': 2,
            'name': 'Local socket',
            'host': 'unix:///var/run/docker.sock',
            'cert-path': '',
            'swarm-mode': False,
            'path-translation-xnat-prefix': '/data/xnat',
            'path-translation-docker-prefix': str(XNAT_ROOT_DIR),
            'pull-images-on-xnat-init': False,
            'container-user': '',
            'auto-cleanup': True,
            'swarm-constraints': [],
            'ping': True})
    
    return container


def launch_docker_registry():
    xnat_docker_network = docker_network()
    dc = docker.from_env()
    try:
        image = dc.images.get(DOCKER_REGISTRY_IMAGE)
    except docker.errors.ImageNotFound:
        image = dc.images.pull(DOCKER_REGISTRY_IMAGE)

    try:
        container = dc.containers.get(DOCKER_REGISTRY_CONTAINER)
    except docker.errors.NotFound:
        container = dc.containers.run(
            image.tags[0], detach=True,
            ports={'5000/tcp': REGISTRY_PORT},
            network=xnat_docker_network.id,
            remove=True, name=DOCKER_REGISTRY_CONTAINER)
    return container


def stop_xnat():
    launch_xnat().stop()


def stop_docker_registry():
    launch_docker_registry().stop(DOCKER_REGISTRY_CONTAINER)


def docker_network():
    dc = docker.from_env()
    try:
        network = dc.networks.get(DOCKER_NETWORK_NAME)
    except docker.errors.NotFound:
        network = dc.networks.create(DOCKER_NETWORK_NAME)
    return network


def connect():
    return xnat.connect(XNAT_URI, user=XNAT_USER, password=XNAT_PASSWORD)
