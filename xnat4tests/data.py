import os
import typing as ty
import tempfile
import shutil
import zipfile
from contextlib import contextmanager
from pathlib import Path
from xnat.exceptions import XNATResponseError
from .base import connect
from .config import Config
from .utils import logger


AVAILABLE_DATASETS = ["dummydicom", "user-training", "openneuro-t1w", "simple-dir"]


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
        from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import (
            get_image as t1w_syngo,
        )
        from medimages4tests.dummy.dicom.mri.dwi.siemens.skyra.syngo_d13c import (
            get_image as dwi_syngo,
        )
        from medimages4tests.dummy.dicom.mri.fmap.siemens.skyra.syngo_d13c import (
            get_image as fmap_syngo,
        )

        _upload_dicom_data(
            [t1w_syngo(), dwi_syngo(), fmap_syngo()],
            config,
            project_id="dummydicomproject",
            subject_id="dummydicomsubject",
            session_id="dummydicomsession",
        )

    elif dataset == "openneuro-t1w":
        from medimages4tests.mri.neuro.t1w import get_image as openneuro_t1w

        _upload_directly(
            {"t1w": openneuro_t1w()},
            config,
            project_id="OPENNEURO_T1W",
            subject_id="subject01",
            session_id="subject01_MR01",
            resource_name="NIFTI",
        )
        _upload_directly(
            {"t1w": openneuro_t1w()},
            config,
            project_id="OPENNEURO_T1W",
            subject_id="subject02",
            session_id="subject02_MR01",
            resource_name="NIFTI",
        )

    elif dataset == "simple-dir":

        tmp_dir = Path(tempfile.mkdtemp())
        a_dir = tmp_dir / "a-dir"
        a_dir.mkdir()
        for i in range(3):
            a_file = a_dir / f"file{i + 1}.txt"
            a_file.write_text(f"A dummy file - {i + 1}\n")

        _upload_directly(
            {"a-directory": a_dir},
            config,
            project_id="SIMPLE_DIR",
            subject_id="subject01",
            session_id="subject01_1",
            resource_name="DIRECTORY",
        )
        _upload_directly(
            {"a-directory": a_dir},
            config,
            project_id="SIMPLE_DIR",
            subject_id="subject02",
            session_id="subject02_1",
            resource_name="DIRECTORY",
        )

    elif dataset == "user-training":
        from medimages4tests.dummy.dicom.mri.fmap.siemens.skyra.syngo_d13c import (
            get_image as fmap_syngo,
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="CONT01",
            session_id="CONT01_MR01",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="CONT02",
            session_id="CONT02_MR01",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="CONT01",
            session_id="CONT01_MR02",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="CONT02",
            session_id="CONT02_MR02",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="TEST01",
            session_id="TEST01_MR01",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="TEST01",
            session_id="TEST01_MR02",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="TEST02",
            session_id="TEST02_MR01",
        )

        _upload_dicom_data(
            [t1w_syngo(), fmap_syngo()],
            config,
            project_id="TRAINING",
            subject_id="TEST02",
            session_id="TEST02_MR02",
        )

    else:
        raise RuntimeError(
            f"Unrecognised dataset '{dataset}', can be one of {AVAILABLE_DATASETS}"
        )


def _upload_dicom_data(
    to_upload: ty.Union[Path, ty.List[Path], str],
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

        project_uri = f"/data/archive/projects/{project_id}"

        try:
            login.get(project_uri)
        except XNATResponseError:
            login.put(project_uri)
        else:
            logger.debug(
                "'%s' project already exists in test XNAT, skipping add data project",
                project_id,
            )

        # Create subject
        query = {
            "xsiType": "xnat:subjectData",
            "req_format": "qs",
            "xnat:subjectData/label": subject_id,
        }
        login.put(f"{project_uri}/subjects/{subject_id}", query=query)

        try:
            login.get(f"{project_uri}/subjects/{subject_id}/experiments/{session_id}")
        except XNATResponseError:
            pass
        else:
            logger.info(
                "'%s' session in '%s' project already exists in test XNAT, skipping",
                session_id,
                project_id,
            )
            return

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
            login.upload_stream(
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
        experiment_id = login.projects[project_id].experiments[session_id].id
        # Pull headers and create OHIF headers
        # login.put(f"/data/experiments/{experiment_id}?pullDataFromHeaders=true")
        # login.put(f"/data/experiments/{experiment_id}?fixScanTypes=true")
        login.put(f"/data/experiments/{experiment_id}?triggerPipelines=true")


def _upload_directly(
    to_upload: ty.Dict[str, Path],
    config: dict,
    project_id: str,
    subject_id: str,
    session_id: str,
    resource_name: str,
):

    with connect(config) as login:

        project_uri = f"/data/archive/projects/{project_id}"

        try:
            login.get(project_uri)
        except XNATResponseError:
            login.put(project_uri)
        else:
            logger.debug(
                "'%s' project already exists in test XNAT, skipping add data project",
                project_id,
            )

        # Create subject
        query = {
            "xsiType": "xnat:subjectData",
            "req_format": "qs",
            "xnat:subjectData/label": subject_id,
        }
        login.put(f"{project_uri}/subjects/{subject_id}", query=query)

        xproject = login.projects[project_id]

        try:
            xsession = login.get(
                f"{project_uri}/subjects/{subject_id}/experiments/{session_id}"
            )
        except XNATResponseError:
            xsubject = login.classes.SubjectData(label=subject_id, parent=xproject)
            xsession = login.classes.MrSessionData(label=session_id, parent=xsubject)
        else:
            logger.info(
                "'%s' session in '%s' project already exists in test XNAT, skipping",
                session_id,
                project_id,
            )
            return

        for i, (scan_type, fspath) in enumerate(to_upload.items(), start=1):
            xdataset = login.classes.MrScanData(id=i, type=scan_type, parent=xsession)
            resource = xdataset.create_resource(
                resource_name
            )  # TODO get this resource name from somewhere else
            resource.upload_dir(fspath.parent, method="tar_file")
