#!/usr/bin/python
#
# Copyright 2014 Huawei Technologies Co. Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test cobbler installer module."""

from copy import deepcopy
from mock import Mock
import os
import unittest2


os.environ['COMPASS_IGNORE_SETTING'] = 'true'


from compass.deployment.installers.os_installers.cobbler.cobbler import CobblerInstaller
from compass.tests.deployment.test_data import config_data
from compass.utils import setting_wrapper as setting
reload(setting)


class TestCobblerInstaller(unittest2.TestCase):
    """Test CobblerInstaller methods."""
    def setUp(self):
        super(TestCobblerInstaller, self).setUp()
        self.test_cobbler = self._get_cobbler_installer()
        self.expected_host_vars_dict = {
            "host": {
                "host_id": 1,
                "mac_address": "mac_01",
                "fullname": "server01.test",
                "profile": "Ubuntu-12.04-x86_64",
                "name": "server01",
                "dns": "server01.test.ods.com",
                "os_version": "Ubuntu-12.04-x86_64",
                "reinstall_os": True,
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
                "partition": {
                    "/var": {
                        "vol_size": "20",
                        "vol_percentage": "20%"
                    },
                    "/home": {
                        "vol_size": "50",
                        "vol_percentage": "40%"
                    }
                },
                "language": "EN",
                "gateway": "10.145.88.1",
                "timezone": "UTC"
            }
        }

    def tearDown(self):
        super(TestCobblerInstaller, self).tearDown()
        del self.test_cobbler

    def _get_cobbler_installer(self):
        adapter_info = deepcopy(config_data.adapter_test_config)
        cluster_info = deepcopy(config_data.cluster_test_config)
        hosts_info = deepcopy(config_data.hosts_test_config)
        # In config_data, only hosts with ID 1 and 2 needs to install OS.
        del hosts_info[3]

        CobblerInstaller._get_cobbler_server = Mock()
        CobblerInstaller._get_cobbler_server.return_value = "mock_server"
        CobblerInstaller._get_token = Mock()
        CobblerInstaller._get_token.return_value = "mock_token"
        return CobblerInstaller(adapter_info, cluster_info, hosts_info)

    def test_get_host_tmpl_vars_dict(self):
        host_id = 1
        profile = 'Ubuntu-12.04-x86_64'
        global_vars_dict = self.test_cobbler._get_cluster_tmpl_vars_dict()
        output = self.test_cobbler._get_host_tmpl_vars_dict(host_id,
                                                            global_vars_dict,
                                                            profile=profile)
        self.maxDiff = None
        self.assertDictEqual(self.expected_host_vars_dict, output)

    def test_get_system_config(self):
        expected_system_config = {
            "name": "server01",
            "hostname": "server01",
            "profile": "Ubuntu-12.04-x86_64",
            "gateway": "10.145.88.1",
            "modify_interface": {
                "ipaddress-vnet0": "192.168.1.1",
                "netmask-vnet0": "255.255.255.0",
                "management-vnet0": True,
                "macaddress-vnet0": "mac_01",
                "dns-vnet0": "server01.test.ods.com",
                "static-vnet0": True,
                "ipaddress-vnet1": "172.16.1.1",
                "netmask-vnet1": "255.255.255.0",
                "management-vnet1": False,
                "static-vnet1": True
            },
            "ksmeta":{
                "timezone" : "UTC",
                "partition": "/var 20%;/home 40%",
                "chef_url": "https://127.0.0.1",
                "chef_client_name": "server01.test",
                "chef_node_name": "server01.test",
                "tool": "chef"
            }
        }
        package_config = {
            1:{
                "chef_url": "https://127.0.0.1",
                "chef_client_name": "server01.test",
                "chef_node_name": "server01.test",
                "tool": "chef"
            }
        }
        host_id = 1
        self.test_cobbler.set_package_installer_config(package_config)
        output = self.test_cobbler._get_system_config(host_id,
            self.expected_host_vars_dict)
        self.maxDiff = None
        self.assertEqual(expected_system_config, output)
