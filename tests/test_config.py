

def test_config(config, home_dir):

    assert config.xnat_root_dir == home_dir / "xnat_root"
    assert config.xnat_mnt_dirs == ["plugins"]
    assert config.docker_image == "xnat4tests_test"
    assert config.docker_container == "xnat4tests_test"
    assert config.xnat_port == "8090"
    assert config.registry_port == "5555"
    assert config.build_args.xnat_ver == "1.8.5"
    assert config.build_args.xnat_cs_plugin_ver == "3.2.0"
    assert config.build_args.xnat_batch_launch_plugin_ver == "0.6.0"
    assert config.build_args.java_ms == "256m"
    assert config.build_args.java_mx == "1g"
