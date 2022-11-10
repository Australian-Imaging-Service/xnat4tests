import tempfile
from pathlib import Path
from xnat4tests import connect


def test_launch(config, launched_xnat):

    PROJECT = "MY_TEST_PROJECT"
    SUBJECT = "MY_TEST_SUBJECT"
    SESSION = "MY_TEST_SESSION"

    with connect(config) as login:
        # Create project
        login.put(f"/data/archive/projects/{PROJECT}")

        # Create subject
        xsubject = login.classes.SubjectData(label=SUBJECT, parent=login.projects[PROJECT])
        # Create session
        xsession = login.classes.MrSessionData(label=SESSION, parent=xsubject)

        temp_dir = Path(tempfile.mkdtemp())
        a_file = temp_dir / "a_file.txt"
        with open(a_file, "w") as f:
            f.write("a file")

        xresource = login.classes.ResourceCatalog(
            parent=xsession, label="A_RESOURCE", format="text"
        )
        xresource.upload(str(a_file), "a_file")

        assert [p.name for p in (config.xnat_root_dir / "archive").iterdir()] == [
            PROJECT
        ]
        assert [
            p.name
            for p in (config.xnat_root_dir / "archive" / PROJECT / "arc001").iterdir()
        ] == [SESSION]

