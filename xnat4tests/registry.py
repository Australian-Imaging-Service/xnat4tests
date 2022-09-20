import docker
from .config import config
from .utils import get_cert_dir, docker_network, logger, INTERNAL_DOCKER
from .launch import connect


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
            ports={"5000/tcp": config["registry_port"], "443": "443"},
            network=xnat_docker_network.id,
            remove=True,
            name=config["docker_registry_container"],
            volumes={
                get_cert_dir(): {"bind": "/certs", "mode": "ro"}
            },
            environment={
                "REGISTRY_HTTP_ADDR": "0.0.0.0:443",
                "REGISTRY_HTTP_TLS_CERTIFICATE": "/certs/server.crt",
                "REGISTRY_HTTP_TLS_KEY": "/certs/server.key",
            },
        )

        with connect() as xlogin:
            # Set registry URI, Not working due to limitations in XNAT UI
            xlogin.post(
                "/xapi/docker/hubs",
                json={"name": "testregistry", "url": f"https://{INTERNAL_DOCKER}"},
            )

    return container


def stop_docker_registry():
    launch_docker_registry().stop()
