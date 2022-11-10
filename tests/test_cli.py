import traceback
import yaml
from xnat4tests.cli import cli as x4t_cli
from xnat4tests.base import connect
from xnat4tests.config import Config


def show_cli_trace(result):
    return "".join(traceback.format_exception(*result.exc_info))


def test_xnat_cli(work_dir, xnat_root_dir, cli_runner):

    config_path = work_dir / "test-plugins.yaml"
    root_dir = xnat_root_dir / "test-plugins"
    plugins_dir = root_dir / "home" / "plugins"
    plugins_dir.mkdir()

    test_path = plugins_dir / "test.txt"
    with open(test_path, 'w') as f:
        f.write("test")

    with open(config_path, "w") as f:
        yaml.dump(
            {
                "docker_container": "xnat4tests_testplugins",
                "docker_network_name": "xnat4test_testplugins",
                "xnat_mnt_dirs": ["home/plugins"],
                "xnat_root_dir": str(root_dir),
                "xnat_port": '7978',
            },
            f
        )

    result = cli_runner(
        x4t_cli,
        ["-c", str(config_path), "start", "--keep-mounts"]
    )

    assert result.exit_code == 0, show_cli_trace(result)

    assert connect(Config.load(config_path))

    assert test_path.exists()

    result = cli_runner(
        x4t_cli,
        ["-c", str(config_path), "stop"]
    )

    assert result.exit_code == 0, show_cli_trace(result)

    result = cli_runner(
        x4t_cli,
        ["-c", str(config_path), "start"]
    )

    assert not test_path.exists()  # Should be hidden by mounted directory


def test_registry_cli(config, cli_runner):

    result = cli_runner(
        x4t_cli,
        ["--config", config.loaded_from, "registry", "start"]
    )

    assert result.exit_code == 0, show_cli_trace(result)

    result = cli_runner(
        x4t_cli,
        ["--config", config.loaded_from, "registry", "stop"]
    )

    assert result.exit_code == 0, show_cli_trace(result)
