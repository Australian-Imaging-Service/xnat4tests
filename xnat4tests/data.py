import os
import typing as ty
import tempfile
import shutil
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


AVAILABLE_DATASETS = ["dummydicom"]


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


def add_data(dataset: str, config_name: str or dict = "default"):
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
        raise RuntimeError(
            f"XNAT instance not running at {config.xnat_uri}. "
            f"run `xnat4tests --config {config.loaded_from} start` "
            f"to launch it"
        )

    if dataset == "dummydicom":

        _upload_dicom_data(
            [t1w_syngo(), dwi_syngo(), fmap_syngo()],
            config,
            project_id="dummydicomproject",
            subject_id="dummydicomsubject",
            session_id="dummydicomsession",
        )

    else:
        raise RuntimeError(
            f"Unrecognised dataset '{dataset}', can be one of {AVAILABLE_DATASETS}"
        )


def _upload_dicom_data(
    to_upload: Path or ty.List[Path] or str,
    config: dict,
    project_id: str,
    subject_id: str,
    session_id: str,
):

    if isinstance(to_upload, str):
        to_upload = Path(to_upload)
    if isinstance(to_upload, Path):
        to_upload = [to_upload]

    work_dir = Path(tempfile.mkdtemp())

    with connect(config) as login:

        login.put(f"/data/archive/projects/{project_id}")
        # Create subject
        query = {
            "xsiType": "xnat:subjectData",
            "req_format": "qs",
            "xnat:subjectData/label": subject_id,
        }
        login.put(
            f"/data/archive/projects/{project_id}/subjects/{subject_id}", query=query
        )

        dicoms_dir = work_dir / "dicoms"
        dicoms_dir.mkdir()

        for i, dcm_dir in enumerate(to_upload):
            shutil.copytree(dcm_dir, dicoms_dir / str(i))

        zipped = work_dir / "dicoms.zip"

        with zipfile.ZipFile(
            zipped,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as zfile, set_cwd(dicoms_dir):
            for dcm_dir in dicoms_dir.iterdir():
                for dcm_file in dcm_dir.iterdir():
                    zfile.write(dcm_file.relative_to(dicoms_dir))

        with open(zipped, "rb") as f:
            # Import data
            login.upload(
                "/data/services/import",
                query={
                    "dest": (
                        f"/archive/projects/{project_id}/subjects"
                        f"/{subject_id}/experiments/{session_id}"
                    ),
                    "Direct-Archive": True,
                    "overwrite": True,
                },
                file_=f,
                content_type="application/zip",
                method="post",
            )
