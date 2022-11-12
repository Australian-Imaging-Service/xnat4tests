Xnat4Tests
==========
.. image:: https://github.com/australian-imaging-service/xnat4tests/actions/workflows/test.yml/badge.svg
   :target: https://github.com/Australian-Imaging-Service/xnat4tests/actions/workflows/test.yml
.. image:: https://codecov.io/gh/australian-imaging-service/xnat4tests/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/australian-imaging-service/xnat4tests
.. image:: https://img.shields.io/pypi/v/xnat4tests.svg
   :target: https://pypi.python.org/pypi/xnat4tests/
.. image:: https://img.shields.io/pypi/pyversions/xnat4tests.svg
   :target: https://pypi.python.org/pypi/xnat4tests/
   :alt: Supported Python versions


Xnat4Tests provides a helper functions for testing third party tools that access the XNAT
API or container service, primarily a means to launch a basic XNAT repository instance
within a single Docker container.

The XNAT container service plugin is installed by default and is configured to use
the same Docker host as the XNAT instance.

The ``home/logs``, ``home/work``, ``build``, ``archive``, ``prearchive`` directories are
mounted in from the host under ``$HOME/.xnat4tests/xnat_root/default``
by default, which can be useful for debugging and enables the environment in which
containers run in within XNAT's container service to be mocked.

In addition to the ``start`` function, which launches the XNAT instance, a ``connect``
function is supplied that returns an XnatPy connection object to the test instance

Installation
------------

Docker needs to be installed on your system, see `Get Docker <https://docs.docker.com/get-docker/>`_
for details.

Xnat4Tests is available on PyPI so can be installed with

.. code-block:: bash

    $ pip3 install xnat4tests

or include in your package's ``test_requires`` if you are writing Python tests.

Usage
-----

Command line interface
~~~~~~~~~~~~~~~~~~~~~~

The test XNAT can be launched via the CLI by

.. code-block:: bash

    $ xnat4tests start

This will spin up an empty XNAT instance that can be accessed using the default admin
user account user='admin'/password='admin'. To add some sample data to play with you
can use the `add-data` command

.. code-block:: bash

    $ xnat4tests start
    $ xnat4tests add-data 'dummydicom'

or in a single line

.. code-block:: bash

    $ xnat4tests start --with-data 'dummydicom'

By default, xnat4tests will create a configuration file at `$HOME/.xnat4tests/configs/default.yaml`.
The config file can be adapted to modify the names of the Docker images/containers used, the ports
the containers run on, and which directories are mounted into the container. Multiple
configurations can be used concurrently by saving the config file to a new location and
passing it to the base command, i.e.

.. code-block:: bash

    $ xnat4tests --config /path/to/my/repo/xnat4tests-config.yaml start

To stop or restart the running container you can use ``xnat4tests stop`` and ``xnat4tests
restart`` commands, respectively.


Python API
~~~~~~~~~~

If you are developing Python applications you will typically want to use the API to
launch the XNAT instance using the `xnat4tests.start_xnat` function. An XnatPy connection
session object can be accessed using `xnat4tests.connect` and the instanced stopped
afterwards using `stop_xnat`.

.. code-block:: python

    # Import xnat4tests functions
    from xnat4tests import start_xnat, stop_xnat, connect, Config

    config = Config.load_config("default")

    # Launch the instance (NB: it takes quite while for an XNAT instance to start). If an existing
    # container with the reserved name is already running it is returned instead
    start_xnat(config)

    # Connect to the XNAT instance using XnatPy and run some tests
    with connect(config) as login:
        PROJECT = 'MY_TEST_PROJECT'
        SUBJECT = 'MYSUBJECT'
        SESSION = 'MYSESSION'

        login.put(f'/data/archive/projects/MY_TEST_PROJECT')

        # Create subject
        xsubject = login.classes.SubjectData(label=SUBJECT,
                                             parent=login.projects[PROJECT])
        # Create session
        login.classes.MrSessionData(label=SESSION, parent=xsubject)

    assert [p.name for p in (config.xnat_root_dir / "archive").iterdir()] == [PROJECT]

    # Remove the container after you are done (not strictly necessary)
    stop_xnat(config)

Alternatively, if you are using Pytest then you can set up the connection as
a fixture in your ``conftest.py``, e.g.

.. code-block:: python

    import tempfile
    from pathlib import Path
    from xnat4tests import start_xnat, stop_xnat, connect, Config

    @pytest.fixture(scope="session")
    def xnat_config():
        tmp_dir = Path(tempfile.mkdtemp())
        return Config(
            xnat_root_dir=tmp_dir,
            xnat_port=9999,
            docker_image="myrepo_xnat4tests",
            docker_container="myrepo_xnat4tests",
            build_args={
                "xnat_version": "1.8.5",
                "xnat_cs_plugin_version": "3.2.0",
            },
        )

    @pytest.fixture(scope="session")
    def xnat_uri(xnat_config):
        xnat4tests.start_xnat(xnat_config)
        xnat4tets.add_data("dummydicom")
        yield xnat_config.xnat_uri
        xnat4tests.stop_xnat(xnat_config)
