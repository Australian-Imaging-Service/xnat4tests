from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'docker'

SRC_DIR = ROOT_DIR / 'src'
BUILD_DIR = ROOT_DIR / 'build'
XNAT_ROOT = ROOT_DIR / 'xnat_root'
XNAT_MNT_DIRS = [
    'home/logs', 'home/work', 'build', 'archive', 'prearchive']
DOCKER_IMAGE = 'xnat4tests'
DOCKER_CONTAINER = 'xnat4tests'
DOCKER_HOST = 'localhost'
XNAT_PORT = '8080'  # This shouldn't be changed as it needs to be the same as the internal for the container service to work
DOCKER_REGISTRY_IMAGE = 'registry'
DOCKER_REGISTRY_CONTAINER = 'xnat4tests-docker-registry'
DOCKER_NETWORK_NAME = 'xnat4tests'
REGISTRY_PORT = '80'  # Must be 80 to avoid bug in XNAT CS config
XNAT_URI = f'http://{DOCKER_HOST}:{XNAT_PORT}'
REGISTRY_URI = f'{DOCKER_HOST}:{REGISTRY_PORT}'
XNAT_USER = 'admin'
XNAT_PASSWORD = 'admin'
CONNECTION_ATTEMPTS = 20
CONNECTION_ATTEMPT_SLEEP = 5
