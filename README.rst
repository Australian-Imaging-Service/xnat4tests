Xnat4Tests
----------

Xnat4Tests provides a method for launching a basic XNAT repository instance
within a single Docker image to facilitate the testing API calls and container
service execution by third-party packages.

The 'home/logs', 'home/work', 'build', 'archive', 'prearchive' directories are
mounted in from the host for direct access, which is useful for debugging
and enables the environment in which containers run in within XNAT's container
service to be mocked.

To launch a xnat instance

.. code-block:: python

    from xnat4tests import launch_xnat, stop_xnat, connect

    # Launch the instance (NB: it takes a while for XNAT to start). If an existing
    # container with the same name is already running it is returned instead
    xnat_container = launch_xnat()

    with connect() as login:
        login.put(f'/data/archive/projects/MY_TEST_PROJECT')
        project_names = list(login.projects.keys())

    # Remove the container after you are done (not strictly necessary)
    stop_xnat()

    assert project_names == ['MY_TEST_PROJECT']

