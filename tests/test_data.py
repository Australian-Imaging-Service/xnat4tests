from xnat4tests.base import connect
from xnat4tests.data import add_data


def test_add_data(config, launched_xnat):

    add_data("dummydicom", config_name=config)

    with connect(config) as login:
        xsess = login.projects["dummydicom"].subjects['dummysubject'].experiments['dummysession']

    assert sorted(s.type for s in xsess.scans()) == ["t1w", "dwi", "fmap"]
