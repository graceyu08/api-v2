adapter_test_config = {
    "name": "openstack_icehouse",
    "roles": ["os-controller", "os-compute-worker", "os-network"],
    "os_installer": {
        "name": "cobbler",
        "settings": {
            "cobbler_url": "127.0.0.1",
            "credentials": {
                "username": "cobbler",
                "password": "cobbler"
            },
            "tmpl_dir": "xxx"
        }
    },
    "pk_installer": {
        "name": "chef",
        "settings": {
            "chef_server_url": "127.0.0.1",
            "key_dir": "xxx",
            "client_name": "xxx"
        }
    },
    "metadata": {
        "os_config": {
            "_self": {},
            "general": {
                "_self": {},
                "language": {
                    "_self": {
                        "mapping_to": "language",
                    },
                },
                "timezone": {
                    "_self": {
                        "mapping_to": "timezone"
                    }
                }
            },
            "partition": {
                "_self": {
                    "mapping_to": "partition"
                },
                "$path": {
                    "_self": {},
                    "max_size": {
                        "_self": {}
                    },
                    "size_percentage": {
                        "_self": {}
                    }
                }
            }
        },
        "package_config": {
            "_self": {},
            "security": {
                "_self": {},
                "service_credentials": {
                    "_self": {
                        "mapping_to": "service_credentials"
                    },
                    "image": {
                         "_self": {
                             "mapping_to": "glance"
                         },
                         "username": {
                             "mapping_to": "username"
                         },
                         "password": {
                             "mapping_to": "password"
                         }
                    }
                }
            },
            "network_mapping":{
                "_self": {},
                "management": {
                    "_self": {},
                    "interface": {
                        "_self": {}
                    }
                },
                "public": {
                    "_self": {},
                    "interface": {
                        "_self": {}
                    }
                }
            },
            "roles": {
                "_self": {}
            }
        }
    }
}


cluster_test_config = {
    "cluster_id": 1,
    "os_version": "Ubuntu-12.04-x86_64",
    "cluster_name": "test",
    "os_config": {
        "general": {
            "language": "EN",
            "timezone": "UTC"
        },
        "partition": {
            "/var": {
                "max_size": "20",
                "size_percentage": "20%"
            },
            "/home": {
                "max_size": "50",
                "size_percentage": "40%"
            }
        }
    },
    "package_config": {
        "service_credentials": {
            "image": {
                "username": "glance",
                "password": "glance"
            }
        },
        "network_mapping": {
            "management": {
                "interface": "eth0"
            },
            "public": {
                "interface": "eth1"
            }
        }
    }
}

hosts_test_config = {
    1: {
        "host_id": 1,
        "os_installed": True,
        "reinstall_os": True,
        "os_version": "Ubuntu-12.04-x86_64",
        "mac_address": "mac_01",
        "hostname": "server_01",
        "networks": {
            "interfaces": {
                "eth0": {
                    "ip": "192.168.1.1",
                    "netmask": "255.255.255.0",
                    "is_mgmt": True,
                    "is_promiscuous": False
                },
                "eth1": {
                    "ip": "192.168.1.2",
                    "netmask": "255.255.255.0",
                    "is_mgmt": False,
                    "is_promiscuous": True
                }
            }
        },
        "os_config": {
            "general": {
                "language": "EN",
                "timezone": "UTC"
            },
            "partition": {
                "/var": {
                    "max_size": "20",
                    "size_percentage": "20%"
                },
                "/home": {
                    "max_size": "50",
                    "size_percentage": "40%"
                }
            }
        },
        "package_config": {
            "roles": ["os-controller"]
        }
    },
    2: {
        "host_id": 1,
        "os_installed": True,
        "reinstall_os": True,
        "os_version": "Ubuntu-12.04-x86_64",
        "mac_address": "mac_01",
        "hostname": "server_01",
        "networks": {
            "interfaces": {
                "eth0": {
                    "ip": "192.168.1.1",
                    "netmask": "255.255.255.0",
                    "is_mgmt": True,
                    "is_promiscuous": False
                },
                "eth1": {
                    "ip": "192.168.1.2",
                    "netmask": "255.255.255.0",
                    "is_mgmt": False,
                    "is_promiscuous": True
                }
            }
        },
        "os_config": {
            "general": {
                "language": "EN",
                "timezone": "UTC"
            },
            "partition": {
                "/var": {
                    "max_size": "20",
                    "size_percentage": "20%"
                },
                "/home": {
                    "max_size": "50",
                    "size_percentage": "40%"
                }
            }
        },
        "package_config": {
            "roles": ["os-controller"]
        }
}
