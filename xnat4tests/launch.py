import stat
import shutil
import time
import requests
import docker
import xnat


from .config import CONFIG


def launch_xnat(
        src_dir=CONFIG['src_dir'],
        root_dir=CONFIG['root_dir'],
        build_dir=CONFIG['build_dir'],
        xnat_root_dir=CONFIG['xnat_root_dir'],
        xnat_mnt_dirs=CONFIG['xnat_mnt_dirs'],
        docker_image=CONFIG['docker_image'],
        docker_container=CONFIG['docker_container'],
        docker_host=CONFIG['docker_host'],
        xnat_port=CONFIG['xnat_port'],
        docker_registry_image=CONFIG['docker_registry_image'],
        docker_registry_container=CONFIG['docker_registry_container'],
        docker_network_name=CONFIG['docker_network_name'],
        registry_port=CONFIG['registry_port'],
        xnat_uri=CONFIG['xnat_uri'],
        registry_uri=CONFIG['registry_uri'],
        xnat_user=CONFIG['xnat_user'],
        xnat_password=CONFIG['xnat_password'],
        connection_attempts=CONFIG['connection_attempts'],
        connection_attempt_sleep=CONFIG['connection_attempt_sleep']):
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
        image = dc.images.get(docker_image)
    except docker.errors.ImageNotFound:
        shutil.rmtree(build_dir, ignore_errors=True)
        shutil.copytree(src_dir, build_dir)
        image, _ = dc.images.build(path=str(build_dir), tag=docker_image)
    
    try:
        container = dc.containers.get(docker_container)
    except docker.errors.NotFound:
        volumes = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock',
                                            'mode': 'rw'}}
        # Mount in the XNAT root directory for debugging and to allow access
        # from the Docker host when using the container service
        # Clear previous ROOT directories
        shutil.rmtree(xnat_root_dir, ignore_errors=True)
        for  dname in xnat_mnt_dirs:
            dpath = xnat_root_dir / dname
            dpath.mkdir(parents=True)
            # Set set-group-ID bit so sub-directories (created by root in
            # Docker inherit GID of launching user)
            dpath.chmod(stat.S_IRUSR |
                        stat.S_IWUSR |
                        stat.S_IXUSR |
                        stat.S_IRGRP |
                        stat.S_IWGRP |
                        stat.S_IXGRP |
                        stat.S_IROTH |
                        stat.S_IXOTH |
                        stat.S_ISGID)  
            volumes[str(dpath)] = {'bind': '/data/xnat/' + dname,
                                   'mode': 'rw'}

        container = dc.containers.run(
            image.tags[0], detach=True, ports={
                '8080/tcp': xnat_port},
            remove=True, name=docker_container,
            # Expose the XNAT archive dir outside of the XNAT docker container
            # to simulate what the XNAT container service exposes to running
            # pipelines, and the Docker socket for the container service to
            # to use
            network=docker_network(docker_network_name).id,
            volumes=volumes)


    # Need to give time for XNAT to get itself ready after it has
    # started so we try multiple times until giving up trying to connect
    for attempts in range(1, connection_attempts + 1):
        try:
            login = connect(xnat_uri, xnat_user, xnat_password)
        except (xnat.exceptions.XNATError, requests.ConnectionError):
            if attempts == connection_attempts:
                raise
            else:
                time.sleep(connection_attempt_sleep)
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
            'path-translation-docker-prefix': str(xnat_root_dir),
            'pull-images-on-xnat-init': False,
            'container-user': '',
            'auto-cleanup': True,
            'swarm-constraints': [],
            'ping': True})

        # Set registry URI
        # login.post('/xapi/docker/hubs/1', json={
        #     "name": "testregistry",
        #     "url": f"https://host.docker.internal"})
    
    return container


def launch_docker_registry(docker_registry_image, docker_registry_container,
                           registry_port):
    xnat_docker_network = docker_network()
    dc = docker.from_env()
    try:
        image = dc.images.get(docker_registry_image)
    except docker.errors.ImageNotFound:
        image = dc.images.pull(docker_registry_image)

    try:
        container = dc.containers.get(docker_registry_container)
    except docker.errors.NotFound:
        container = dc.containers.run(
            image.tags[0], detach=True,
            ports={'5000/tcp': registry_port},
            network=xnat_docker_network.id,
            remove=True, name=docker_registry_container)
        
    return container


def stop_xnat():
    launch_xnat().stop()


def stop_docker_registry(docker_registry_container):
    launch_docker_registry().stop(docker_registry_container)


def docker_network(docker_network_name):
    dc = docker.from_env()
    try:
        network = dc.networks.get(docker_network_name)
    except docker.errors.NotFound:
        network = dc.networks.create(docker_network_name)
    return network


def connect(xnat_uri, xnat_user, xnat_password):
    return xnat.connect(xnat_uri, user=xnat_user, password=xnat_password)
