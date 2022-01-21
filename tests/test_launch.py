
import tempfile
from pathlib import Path
import pytest
from xnat4tests import launch_xnat, stop_xnat, connect, config


@pytest.fixture(scope='session')
def login():
    launch_xnat()
    yield connect()
    stop_xnat()


def test_launch(login):

    PROJECT = 'MY_TEST_PROJECT'   
    SUBJECT = 'MY_TEST_SUBJECT'
    SESSION = 'MY_TEST_SESSION'

    # Create project
    login.put(f'/data/archive/projects/{PROJECT}')

    # Create subject
    xsubject = login.classes.SubjectData(label=SUBJECT,
                                            parent=login.projects[PROJECT])
    # Create session
    xsession = login.classes.MrSessionData(label=SESSION, parent=xsubject)

    temp_dir = Path(tempfile.mkdtemp())
    a_file = temp_dir / 'a_file.txt'
    with open(a_file, 'w') as f:
        f.write('a file')
    
    xresource = login.classes.ResourceCatalog(
        parent=xsession, label='A_RESOURCE', format='text')
    xresource.upload(str(a_file), 'a_file')

    assert [p.name for p in (config.XNAT_ROOT_DIR / 'archive').iterdir()] == [PROJECT]
    assert [p.name for p in (config.XNAT_ROOT_DIR / 'archive' / PROJECT / 'arc001').iterdir()] == [SESSION]
