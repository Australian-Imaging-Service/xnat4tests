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


def test_add_nifti(config, launched_xnat):

    add_data("openneuro-t1w", config_name=config)

    with connect(config) as login:
        xsess1 = (
            login.projects["OPENNEURO_T1W"]
            .subjects["subject01"]
            .experiments["subject01_MR01"]
        )

        assert sorted(s.type for s in xsess1.scans.values()) == [
            "t1w",
        ]

        xsess2 = (
            login.projects["OPENNEURO_T1W"]
            .subjects["subject02"]
            .experiments["subject02_MR01"]
        )

        assert sorted(s.type for s in xsess2.scans.values()) == [
            "t1w",
        ]


def test_simple_dir(config, launched_xnat):

    add_data("simple-dir", config_name=config)

    with connect(config) as login:
        xsess1 = (
            login.projects["SIMPLE_DIR"]
            .subjects["subject01"]
            .experiments["subject01_1"]
        )

        assert sorted(s.type for s in xsess1.scans.values()) == [
            "a-directory",
        ]

        xsess2 = (
            login.projects["SIMPLE_DIR"]
            .subjects["subject02"]
            .experiments["subject02_1"]
        )

        assert sorted(s.type for s in xsess2.scans.values()) == [
            "a-directory",
        ]
