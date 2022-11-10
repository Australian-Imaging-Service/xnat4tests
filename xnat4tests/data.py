import os
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import (
    get_image as t1w_syngo,
)
from medimages4tests.dummy.dicom.mri.dwi.siemens.skyra.syngo_d13c import (
    get_image as dwi_syngo,
)
from medimages4tests.dummy.dicom.mri.fmap.siemens.skyra.syngo_d13c import (
    get_image as fmap_syngo,
)
from .base import connect
from .config import Config


@contextmanager
def set_cwd(path):
    """Sets the current working directory to `path` and back to original
    working directory on exit

    Parameters
    ----------
    path : str
        The file system path to set as the current working directory
    """
    pwd = Path.cwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pwd)


def add_data(
    dataset: str,
    config_name: str or dict = "default"
):
    """Uploads sample test data into the XNAT repository for use in test regimes

    Parameters
    ----------
    dataset : str
        name of the dataset to add. Can be one of: ["dummydicom"]
    config_name : str or dict, optional
        the configuration that specifies how to connect to the XNAT instance
    """
    config = Config.load(config_name)

    try:
        connect(config)
    except Exception:
        raise RuntimeError(f"XNAT instance not running at {config.xnat_uri}. "
                           f"run `xnat4tests --config {config.loaded_from} start` "
                           f"to launch it")

    if dataset == "dummydicom":

        to_upload = Path(tempfile.mkdtemp()) / "to_upload"

        t1w_syngo(out_dir=to_upload / "t1w")
        dwi_syngo(out_dir=to_upload / "dwi")
        fmap_syngo(out_dir=to_upload / "fmap")

        _upload_dicom_data(
            to_upload,
            config,
            project_id="dummydicomproject",
            subject_id="dummydicomsubject",
            session_id="dummydicomsession",
        )


def _upload_dicom_data(
    to_upload: Path,
    config: dict,
    project_id: str,
    subject_id: str,
    session_id: str,
):
    work_dir = Path(tempfile.mkdtemp())

    zipped_file = work_dir / "to_upload.zip"

    with zipfile.ZipFile(
        zipped_file,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        allowZip64=True,
    ) as zfile, set_cwd(to_upload):
        for dcm_dir in to_upload.iterdir():
            for dcm_file in dcm_dir.iterdir():
                zfile.write(dcm_file.relative_to(to_upload))

    # Add project, needs to be in a separate connection as it is only visible when
    # you log in again
    with connect(config) as login:
        login.put(f"/data/archive/projects/{project_id}")

    with connect(config) as login, open(zipped_file) as f:
        # Create subject
        query = {
            "xsiType": "xnat:subjectData",
            "req_format": "qs",
            "xnat:subjectData/label": subject_id,
        }
        login.put(f"/data/archive/projects/{project_id}/subjects/{subject_id}",
                  query=query)

        # Import data
        login.put(
            "/data/service/import",
            json={
                "dest": (
                    f"/archive/projects/{project_id}/subjects"
                    f"/{subject_id}/experiments/{session_id}"
                ),
                "import-handler": "DICOM-zip",
                "Direct-Archive": True,
            },
            data=f,
        )
