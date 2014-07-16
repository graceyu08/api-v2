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
"""Module to get configs from provider and isntallers and update
   them to provider and installers.
"""
import imp
import logging
import os

from compass.db import db_api
from compass.deployment.installers.installer import PKInstaller
from compass.deployment.installers.installer import OSInstaller
from compass.utils import util


class DeployManager(object):
    def __init__(self, adapter_info, cluster_info, hosts_info):
        os_installer_name = adapter_info['os_installer']['name']
        pk_installer_name = adapter_info['pk_installer']['name']

        os_hosts_info = self._get_hosts_for_os_installation(hosts_info)

        self.os_installer = self._get_os_installer(os_installer_name,
                                                   adapter_info,
                                                   cluster_info,
                                                   os_hosts_info)
        self.pk_installer = self._get_package_installer(pk_installer_name,
                                                        adapter_info,
                                                        cluster_info,
                                                        hosts_info)


    def _get_os_installer(self, installer_name, adapter_info, cluster_info,
                          hosts_info):
        try:
            installer_class = OSInstaller.get_os_installer(installer_name)
        except Exception as ex:
            raise Exception(ex.message)

        installer = installer_class(adapter_info, cluster_info, hosts_info)
        return installer

    def _get_package_installer(self, installer_name, adapter_info,
                               cluster_info, hosts_info):
        try:
            installer_class = PKInstaller.get_package_installer(installer_name)
        except Exception as ex:
            raise Exception(ex.message)

        installer = installer_class(adapter_info, cluster_info, hosts_info)
        return installer

    def clean_progress(self):
        """Clean previous installation log and progress."""
        # Clean DB
        db_api.cluster.clean_progress(self.cluster_id)
        db_api.cluster_host.clean_progress(self.cluster_id, self.host_id_list)

        # OS installer cleans previous installing progress.
        if self.os_installer:
            self.os_installer.clean_progress()

        # Package installer cleans previous installing progress.
        if self.pk_installer:
            self.package_installer.clean_progress()

    def prepare_for_deploy(self):
        self.clean_progress()

    def deploy(self):
        """Deploy the cluster."""
        if self.pk_installer:
            # generate target system config which will be installed by OS
            # installer right after OS installation is completed.
            pk_instl_conf = self.package_installer.generate_installer_config()
            pk_deploy_config = self.package_installer.deploy()
            # TODO
            self.save_pk_deploy_config(pk_deploy_config)

        if self.os_installer:
            # Send package installer config info to OS installer.
            if pk_instl_conf:
                self.os_installer.set_package_installer_config(pk_instl_conf)

            # start to deploy OS
            os_deploy_config = self.os_installer.deploy()
            # TODO
            self.save_os_deploy_config(os_deploy_config)

    def save_pk_deploy_config(self, packge_deploy_config):
        """Save package config to DB"""
        # Sava cluster package config to cluster deploy config column
        # Save each host package config to host deploy config column
        pass

    def save_os_deploy_config(self, os_deploy_config):
        """Save each host's OS deploy config to its deploy config column."""
        pass

    def redeploy(self):
        if self.os_installer:
            self.os_installer.redeploy()

        if self.package_installer:
            self.package_installer.redeploy()

    def remove_hosts(self):
        """Remove hosts from both OS and package installlers server side."""
        pass

    def remove_cluster(self):
        """Remove all hosts from both OS and package installlers server side.
        """
        pass

    def powerOn(self):
        pass

    def powerOff(self):
        pass

    def reset(self):
        pass

    def _get_hosts_for_os_installation(self, hosts_info):
        """Get info of hosts which need to install/reinstall OS."""
        hosts_list = {}
        for host_id in hosts_info:
            os_installed_flag = hosts_info[host_id]["os_installed"]
            reinstall_os_flag = hosts_info[host_id]["reinstall_os"]
            if os_installed_flag and not reinstall_os_flag:
                continue

            hosts_list[host_id] = hosts_info[host_id]

        return hosts_list
