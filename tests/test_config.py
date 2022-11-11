def test_config(config, home_dir):

    assert config.xnat_root_dir == home_dir / "xnat_root" / "test-config"
    assert config.xnat_mnt_dirs == [
        "home/logs",
        "home/work",
        "build",
        "archive",
        "prearchive",
    ]
    assert config.docker_image == "xnat4tests_unittest"
    assert config.docker_container == "xnat4tests_unittest"
    assert config.xnat_port == "8090"
    assert config.registry_port == "5555"
    assert config.build_args.xnat_version == "1.8.6"
    assert config.build_args.xnat_cs_plugin_version == "3.2.0"
    assert config.build_args.xnat_batch_launch_plugin_version == "0.6.0"
    assert config.build_args.java_ms == "256m"
    assert config.build_args.java_mx == "1g"
