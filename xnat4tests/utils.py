import sys
import logging
import docker
from .config import config


logger = logging.getLogger("xnat4tests")

xnat_uri = f"http://{config['docker_host']}:{config['xnat_port']}"
registry_uri = f"{config['docker_host']}"

if sys.platform == "linux":
    INTERNAL_DOCKER = "172.17.0.1"  # Linux + GH Actions
else:
    INTERNAL_DOCKER = "host.docker.internal"  # Mac/Windows local debug


def get_cert_dir():
    """Self signs OpenSSL certs to be used by docker registry"""
    cert_dir = config["docker_registry_cert_dir"]
    if not cert_dir.exists():
        cert_dir.mkdir()

        dc = docker.from_env()

        openssl = dc.images.pull("alpine/openssl")

        # Here we reuse the XNAT docker container to generate SSL keys (which has
        # openssl installed in it for this reason)
        openssl.run(
            'openssl req -x509 '
            '-sha256 -days 356 '
            '-nodes '
            '-newkey rsa:2048 '
            f'-subj "/CN={INTERNAL_DOCKER}/C=AU/L=Sydney" '
            '-keyout rootCA.key -out rootCA.crt'
        )

        with open(cert_dir / "csr.conf", 'w') as f:
            f.write(CSR_CONF)

        openssl.run(
            "openssl req -new -key server.key -out server.csr -config csr.conf"
        )

        with open(cert_dir / "cert.conf", 'w') as f:
            f.write(CERT_CONF)

        openssl.run(
            "openssl x509 -req "
            "-in server.csr "
            "-CA rootCA.crt -CAkey rootCA.key "
            "-CAcreateserial -out server.crt "
            "-days 365 "
            "-sha256 -extfile cert.conf"
        )


def docker_network():
    dc = docker.from_env()
    try:
        network = dc.networks.get(config["docker_network_name"])
    except docker.errors.NotFound:
        network = dc.networks.create(config["docker_network_name"])
    return network


CSR_CONF = f"""
[req]
default_bits  = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
countryName = XX
stateOrProvinceName = N/A
localityName = N/A
organizationName = Self-signed certificate
commonName = 120.0.0.1: Self-signed certificate

[req_ext]
subjectAltName = @alt_names

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = {INTERNAL_DOCKER}

"""

CERT_CONF = """
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = {INTERNAL_DOCKER}
"""
