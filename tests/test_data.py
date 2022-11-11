from xnat4tests.base import connect
from xnat4tests.data import add_data


def test_add_data(config, launched_xnat):

    add_data("dummydicom", config_name=config)

    with connect(config) as login:
        xsess = (
            login.projects["dummydicomproject"]
            .subjects["dummydicomsubject"]
            .experiments["dummydicomsession"]
        )

        assert sorted(s.type for s in xsess.scans.values()) == [
            "R-L MRtrix 60 directions interleaved B0 ep2d_diff_p2",
            "gre_field_mapping 3mm",
            "t1_mprage_sag_p2_iso_1",
        ]
