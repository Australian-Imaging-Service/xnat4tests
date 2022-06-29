from pathlib import Path

ROOT_DIR = Path.home() / '.xnat4tests'
ROOT_DIR.mkdir(exist_ok=True)

DOCKER_HOST = 'localhost'
XNAT_PORT = '8080'

CONFIG = {
    'src_dir': Path(__file__).parent / 'docker-src',
    'root_dir': ROOT_DIR,
    'build_dir': ROOT_DIR / 'build',
    'xnat_root_dir': ROOT_DIR / 'xnat_root',
    'xnat_mnt_dirs': ['home/logs', 'home/work', 'build', 'archive', 'prearchive'],
    'docker_image': 'xnat4tests',
    'docker_container': 'xnat4tests',
    'docker_host': DOCKER_HOST,
    'xnat_port': XNAT_PORT,  # This shouldn't be changed as it needs to be the same as the internal for the container service to work,
    'docker_registry_image': 'registry',
    'docker_registry_container': 'xnat4tests-docker-registry',
    'docker_network_name': 'xnat4tests',
    'registry_port': '80',  # Must be 80 to avoid bug in XNAT CS config,
    'xnat_uri': f'http://{DOCKER_HOST}:{XNAT_PORT}',
    'registry_uri': f'{DOCKER_HOST}',  # : {REGISTRY_PORT}',
    'xnat_user': 'admin',
    'xnat_password': 'admin',
    'connection_attempts': 20,
    'connection_attempt_sleep': 5}
