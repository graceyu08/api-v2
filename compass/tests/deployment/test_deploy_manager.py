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

"""Test deploy_manager module."""


import os
import unittest2


os.environ['COMPASS_IGNORE_SETTING'] = 'true'


from copy import deepcopy
from compass.utils import setting_wrapper as setting
reload(setting)


from compass.deployment.deploy_manager import DeployManager
from compass.deployment.installers.installer import PKInstaller
from compass.deployment.installers.installer import OSInstaller
from compass.tests.deployment.test_data import config_data


class DummyOSInstaller(OSInstaller):
    NAME = 'test_cobbler'

    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(DummyOSInstaller, self).__init__()
        self.hosts_info = hosts_info

OSInstaller.register(DummyOSInstaller)

class DummyPKInstaller(PKInstaller):
    NAME = 'test_chef'
    
    def __init__(self, adapter_info, cluster_info, hosts_info):
        super(DummyPKInstaller, self).__init__()

PKInstaller.register(DummyPKInstaller)

class TestDeployManager(unittest2.TestCase):
    """Test DeployManager methods."""
    def setUp(self):
        super(TestDeployManager, self).setUp()

    def tearDown(self):
        super(TestDeployManager, self).tearDown()

    def test_init_DeployManager(self):
        adapter_info = deepcopy(config_data.adapter_test_config)
        cluster_info = deepcopy(config_data.cluster_test_config)
        hosts_info = deepcopy(config_data.hosts_test_config)

        # Test if DeployManager is instantiated successfully
        test_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        self.assertIsNotNone(test_manager)

        # Test if installers are the expected ones.
        expected_pk_installer_name = adapter_info['pk_installer']['name']
        expected_os_installer_name = adapter_info['os_installer']['name']

        pk_installer_name = test_manager.pk_installer.NAME
        os_installer_name = test_manager.os_installer.NAME
        self.assertEqual(expected_pk_installer_name, pk_installer_name)
        self.assertEqual(expected_os_installer_name, os_installer_name)

        # Test hepler function _get_hosts_for_os_installation return correct
        # number of hosts config for os deployment. In config_data, two out of
        # three hosts need to install OS.
        hosts_list = test_manager._get_hosts_for_os_installation(hosts_info)
        self.assertEqual(2, len(hosts_list))
