
from xnat4tests import launch_xnat, stop_xnat, connect, config


def test_launch():

    PROJECT = 'MY_TEST_PROJECT'   
    SUBJECT = 'MY_TEST_SUBJECT'
    SESSION = 'MY_TEST_SESSION'

    # Launch the instance (NB: it takes quite while for an XNAT instance to start). If an existing
    # container with the reserved name is already running it is returned instead
    launch_xnat()

    # Run your tests
    with connect() as login:
        # Create project
        login.put(f'/data/archive/projects/{PROJECT}')

        # Create subject
        xsubject = login.classes.SubjectData(label=SUBJECT,
                                             parent=login.projects[PROJECT])
        # Create session
        login.classes.MrSessionData(label=SESSION, parent=xsubject)

    assert [p.name for p in (config.XNAT_ROOT_DIR / 'archive').iterdir()] == [PROJECT]

    # Remove the container after you are done (not strictly necessary)
    stop_xnat()
    