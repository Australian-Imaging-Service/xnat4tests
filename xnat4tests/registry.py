import docker
from .utils import logger
from .config import load_config
from .base import docker_network, connect


def start_registry(config_name="default"):

    config = load_config(config_name)

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

        with connect() as xlogin:
            # Set registry URI, Not working due to limitations in XNAT UI
            xlogin.post(
                "/xapi/docker/hubs",
                json={"name": "testregistry", "url": "http://host.docker.internal"},
            )

    return container


def stop_registry(config_name="default"):

    config = load_config(config_name)

    dc = docker.from_env()
    try:
        container = dc.containers.get(config["docker_registry_container"])
    except docker.errors.NotFound:
        pass
    else:
        container.stop()
