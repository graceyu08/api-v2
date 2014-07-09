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
    def __init__(self, cluster_id, hosts_id_list, config):
        self.cluster_id = cluster_id
        self.hosts_id_list = hosts_id_list
        self.adapter_info = self._get_adapter_info(cluster_id)

        os_installer_info = self.adapter_info['os_installer']
        pk_installer_info = self.adapter_info['pk_installer']
        
        self.deploy_config = self._get_deploy_config(config)

        self.os_installer = self._get_installer(os_installer_info)
        self.pk_installer = self._get_installer(pk_installer_info)


    def _get_os_installer(self, installer_info):
        installer_name = installer_info['name']
        try:
            installer_class = OSInstaller.get_os_installer(installer_name)
        except Exception as ex:
            raise Exception(ex.message)

        installer = installer_class(installer_info['settings'],
                                    self.depoly_config)
        return installer

    def _get_package_installer(self, installer_info):
        installer_name = installer_info['name']
        try:
            installer_class = PKInstaller.get_package_installer(installer_name)
        except Exception as ex:
            raise Exception(ex.message)

        installer = installer_class(installer_info['settings'],
                                    self.deploy_config)
        return installer

    def _get_deploy_config(self, config):
        """Generate deloy config based on input config by filling fullname and
           dns name.
           The output deploy config format will be:
           {
              "cluster": {
                  "cluster_id": 1,
                  "cluster_name": "xxx",
                  "deploy_config": {
                      "package_config": {
                          "network_mapping": {
                            ...  
                          }  
                      },
                      "roles_mapping": {
                          "controller": {
                              "management": {
                                  "interface": "eth0", 
                                  "ip": "xxx"
                              },
                              ....
                          }
                      }
                  }
              },
              "hosts": {
                  1($host_id) :{
                     "host_id": 1,
                     "os_version": "CentOS"
                     "fullname": "xxx",
                     "dns": "xxx",
                     "mac_address": "xxxx",
                     "hostname": "xxx",
                     "networks": {
                         "interfaces": {
                             "eth0":{
                                 "ip": "xxx",
                                 "netmask": "xxx",
                                 "is_mgmt": True
                             },
                             ....
                         }
                     },
                     "deploy_config": {
                         "os_config" :{
                             .......
                         },
                         "package_config": {
                            ....
                         } 
                     }
                  },
                  ...
              }
           }
        """
        pass

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
        adapter_name = self.adapter_info['name']
        os_installer_config = {}
        if self.pk_installer:
            # generate target system config which will be installed by OS
            # installer right after OS installation is completed.
            pk_instl_conf = self.package_installer.generate_installer_config()
        
        if self.os_installer:
            self.os_installer.set_config(self._get_os_config())
            os_version = self.adapter_info['os_version']
            # Send package installer config info to OS installer.
            if os_installer_config:
                self.os_installer.set_package_installer_config(pk_instl_conf)

            # start to deploy OS    
            os_deploy_config = self.os_installer.deploy(os_version)
            # TODO
            self.save_os_deploy_config(os_deploy_config)

        if self.package_installer:
            pk_deploy_config = self.package_installer.deploy(adapter_name)
            # TODO
            self.save_pk_deploy_config(pk_deploy_config)


            
    def redeploy_os(self):
        """Redeploy OS without modifying OS config."""
        if not self.os_installer:
            raise Exception("No OS installer found!")
        os_config = self._get_os_config(redeploy=True)
        self.os_installer.redeploy(os_config)

    def redeploy_target_system(self):
        """Redeploy the target system without modifying package config."""
        pass

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

    def _get_adapter_info(self, cluster_id):
        """Get adapter information. Return a dictionary as below,
           {
              "adapter_name": "xxx",
              "roles": [...],
              "metadata": {
                  "os_config": {
                      ...  
                  },
                  "package_config": {
                      ...  
                  }
              },
              "os_installer": {
                  "name": "cobbler",
                  "settings": {....}
              },
              "pk_installer": {
                  "name": "chef",
                  "settings": {....}
              }
           }
        """
        pass

    def _get_hosts_for_os_installation(self):
        os_needed_hosts = {}
        hosts = self.deploy_config["hosts"]
        for host_id in hosts:
            os_installed_flag = hosts[host_id]["os_installed"]
            reinstall_os_flag = hosts[host_id]["reinstall_os"]
            if os_installed_flag and not reinstall_os_flag:
                continue
            
            os_needed_hosts[host_id] = hosts[host_id]

        return os_needed_hosts



