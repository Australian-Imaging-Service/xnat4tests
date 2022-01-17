Xnat4Tests
----------

Xnat4Tests provides a method for launching a basic XNAT repository instance
within a single Docker image to facilitate the testing API calls and container
service execution by third-party packages.

The 'home/logs', 'home/work', 'build', 'archive', 'prearchive' directories are
mounted in from the host for direct access under ``xnat4tests.config.XNAT_ROOT_DIR``,
which can be useful for debugging and enables the environment in which containers
run in within XNAT's container service to be mocked.

To launch an XNAT instance

.. code-block:: python

    # Import xnat4tests functions
    from xnat4tests import launch_xnat, stop_xnat, connect, config

    # Launch the instance (NB: it takes quite while for an XNAT instance to start). If an existing
    # container with the reserved name is already running it is returned instead
    xnat_container = launch_xnat()

    # Run your tests
    with connect() as login:
        login.put(f'/data/archive/projects/MY_TEST_PROJECT')

    assert [p.name for p in (config.XNAT_ROOT_DIR / 'archive', 'arc001').iterdir()] == ['MY_TEST_PROJECT']

    # Remove the container after you are done (not strictly necessary)
    stop_xnat()
