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

"""Module to manage and access cluster, hosts and adapter config.
"""
import logging


class BaseConfigManager(object):

    def __init__(self, adapter_info, cluster_info, hosts_info):
        self.adapter_info = adapter_info
        self.cluster_info = cluster_info
        self.hosts_info = hosts_info

    def get_cluster_id(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info['cluster']['cluster_id']

    def get_os_version(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info["os_version"]

    def get_host_id_list(self):
        if not self.hosts_info:
            logging.info("hosts config is None or {}")
            return None

        return self.hosts_info.keys()

    def get_cluster_os_config(self):
        pass

    def get_cluster_package_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info["cluster"]["deploy_config"]["package_config"]

    def get_cluster_roles_mapping(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        if "roles_mapping" not in self.cluster_info['deploy_config']:
            logging.info("No 'roles_mapping' found in the cluster config!")
            return None

        return self.cluster_info['deploy_config']['roles_mapping']

    def _get_host_info(self, host_id):
        if not self.hosts_info:
            logging.info("hosts config is None or {}")
            return None

        if host_id not in self.hosts_info:
            logging.info("Cannot find host, ID is '%s'", host_id)
            return None

        return self.hosts_info[host_id]


    def get_host_fullname(self, host_id):
        if not self._get_host_info(host_id):
            return None
        host_info = self._get_host_info(host_id)
        return host_info['fullname']

    def get_host_dns(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info['dns']

    def get_host_mac_address(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info['mac_address']

    def get_host_hostname(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info['hostname']

    def get_host_interfaces(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        nics = host_info['networks']["interfaces"]
        return nics.keys()

    def _get_host_interface_config(self, host_id, interface):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)

        if interface not in host_info['networks']:
           logging.info("Cannot find NIC '%s'", interface)
           return None

        return host_info["networks"]["interfaces"][interface]

    def get_host_interface_ip(self, host_id, interface):
        if not self._get_host_interface_config(host_id, interface):
            return None

        interface_config = self._get_host_interface_config(host_id, interface)
        return interface_config["ip"]

    def get_host_interface_netmask(self, host_id, interface):
        if not self._get_host_interface_config(host_id, interface):
            return None

        interface_config = self._get_host_interface_config(host_id, interface)
        return interface_config["netmask"]

    def get_host_os_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info["deploy_config"]["os_config"]

    def get_host_package_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info["deploy_config"]["package_config"]

    def get_adapter_name(self):
        return self.adapter_info['name']

    def get_adapter_roles(self):
        return self.adapter_info['roles']

    def get_os_installer_settings(self):
        return self.adapter_info['os_installer']['settings']

    def get_pk_installer_settings(self):
        return self.adapter_info['pk_installer']['settings']

    def get_os_config_metadata(self):
        return self.adapter_info['metadata']['os_config']

    def get_pk_config_meatadata(self):
        return self.adapter_info['metadata']['package_config']
