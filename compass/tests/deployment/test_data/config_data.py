import os


curr_dir = os.path.dirname(os.path.realpath(__file__))
cobbler_system_tmpl_dir = os.path.join(curr_dir, 'templates/cobbler')
chef_tmpl_dir = os.path.join(os.path.join(curr_dir, 'templates/chef'),
                             "openstack_icehouse")

adapter_test_config = {
    "name": "openstack_icehouse",
    "roles": ["os-controller", "os-compute-worker", "os-network"],
    "os_installer": {
        "name": "test_cobbler",
        "settings": {
            "cobbler_url": "127.0.0.1",
            "credentials": {
                "username": "cobbler",
                "password": "cobbler"
            },
            "tmpl_dir": cobbler_system_tmpl_dir
        }
    },
    "pk_installer": {
        "name": "test_chef",
        "settings": {
            "chef_server_url": "127.0.0.1",
            "key_dir": "xxx",
            "client_name": "xxx",
            "tmpl_dir": chef_tmpl_dir
        }
    },
    "metadata": {
        "os_config": {
            "_self": {},
            "general": {
                "_self": {"mapping_to": ""},
                "language": {
                    "_self": {
                        "mapping_to": "language",
                    },
                },
                "timezone": {
                    "_self": {
                        "mapping_to": "timezone"
                    }
                },
                "default_gateway": {
                    "_self": {
                        "mapping_to": "gateway"    
                    }    
                },
                "domain": {
                    "_self": {"mapping_to": ""}
                }
            },
            "partition": {
                "_self": {
                    "mapping_to": "partition"
                },
                "$path": {
                    "_self": {"mapping_to": ""},
                    "max_size": {
                        "_self": {"mapping_to": "vol_size"}
                    },
                    "size_percentage": {
                        "_self": {"mapping_to": "vol_percentage"}
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
                    "rabbit_mq": {
                         "_self": {
                             "mapping_to": "mq"
                         },
                         "username": {
                             "_self": {
                                 "mapping_to": "username"
                             }
                         },
                         "password": {
                             "_self": {
                                 "mapping_to": "password"
                             }
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
            "timezone": "UTC",
            "default_gateway": "192.168.2.1",
            "domain": "ods.com"
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
        "security": {
            "service_credentials": {
                "rabbit_mq": {
                    "username": "guest",
                    "password": "test"
                }
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
        "os_installed": False,
        "reinstall_os": False,
        "os_version": "Ubuntu-12.04-x86_64",
        "mac_address": "mac_01",
        "hostname": "server_01",
        "networks": {
            "interfaces": {
                "vnet0": {
                    "ip": "192.168.1.1",
                    "netmask": "255.255.255.0",
                    "is_mgmt": True,
                    "is_promiscuous": False,
                    "subnet": "192.168.1.0/24"
                },
                "vnet1": {
                    "ip": "172.16.1.1",
                    "netmask": "255.255.255.0",
                    "is_mgmt": False,
                    "is_promiscuous": True,
                    "subnet": "172.16.1.0/24"
                }
            }
        },
        "os_config": {
            "general": {
                "language": "EN",
                "timezone": "UTC",
                "default_gateway": "192.168.2.1",
                "domain": "ods.com"
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
            "network_mapping": {                                                                                                          
                "management": {                                                    
                    "interface": "vnet0"                                            
                },                                                                 
                "public": {                                                        
                    "interface": "vnet1"                                            
                }                                                                  
            },
            "roles": ["os-controller"]
        }
    },
    2: {
        "host_id": 2,
        "os_installed": True,
        "reinstall_os": True,
        "os_version": "Ubuntu-12.04-x86_64",
        "mac_address": "mac_02",
        "hostname": "server_02",
        "networks": {
            "interfaces": {
                "eth0": {
                    "ip": "192.168.1.2",
                    "netmask": "255.255.255.0",
                    "is_mgmt": True,
                    "is_promiscuous": False,
                    "subnet": "192.168.1.0/24"
                },
                "eth1": {
                    "ip": "172.16.1.2",
                    "netmask": "255.255.255.0",
                    "is_mgmt": False,
                    "is_promiscuous": True,
                    "subnet": "172.16.1.0/24"
                }
            }
        },
        "os_config": {
            "general": {
                "language": "EN",
                "timezone": "UTC",
                "default_gateway": "192.168.2.1",
                "domain": "ods.com"
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
            "roles": ["os-compute", "os-network"]
        }
    },
    3: {
        "host_id": 3,
        "os_installed": True,
        "reinstall_os": False,
        "os_version": "Ubuntu-12.04-x86_64",
        "mac_address": "mac_03",
        "hostname": "server_03",
        "networks": {
            "interfaces": {
                "eth0": {
                    "ip": "192.168.1.3",
                    "netmask": "255.255.255.0",
                    "is_mgmt": True,
                    "is_promiscuous": False,
                    "subnet": "192.168.1.0/24"
                },
                "eth1": {
                    "ip": "172.16.1.3",
                    "netmask": "255.255.255.0",
                    "is_mgmt": False,
                    "is_promiscuous": True,
                    "subnet": "172.16.1.0/24"
                }
            }
        },
        "os_config": {
            "general": {
                "language": "EN",
                "timezone": "UTC",
                "default_gateway": "192.168.2.1",
                "domain": "ods.com"
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
            "roles": ["os-network"]
        }
    }
}
