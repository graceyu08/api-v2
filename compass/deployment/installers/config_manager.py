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
    CLUSTER_ID = 'cluster_id'
    OS_VERSION = 'os_version'
    CLUSTER_NAME = 'cluster_name'
    DEPLOY_CONFIG = 'deploy_config'
    OS_CONFIG = 'os_config'
    PK_CONFIG = 'package_config'
    NETWORK_MAPPING = 'network_mapping'
    ROLES_MAPPING = 'roles_mapping'
    HOST_ID = 'host_id'
    OS_INSTALLED_FLAG = 'os_installed'
    REINSTALL_OS_FLAG = 'reinstall_os'
    FULLNAME = 'fullname'
    DNS = 'dns'
    MAC_ADDR = 'mac_address'
    HOSTNAME = 'hostname'
    NETWORKS = 'networks'
    INTERFACES = 'interfaces'
    IP_ADDR = 'ip'
    NETMASK = 'netmask'
    DOMAIN = 'domain'
    ROLES = 'roles'
    OS_CONFIG_GENERAL = 'general'
    ADAPTER_NAME = 'name'
    OS_INSTALLER = 'os_installer'
    PK_INSTALLER = 'pk_installer'
    INSTALLER_SETTINGS = 'settings'
    METADATA = 'metadata'

    def __init__(self, adapter_info, cluster_info, hosts_info):
        self.adapter_info = adapter_info
        self.cluster_info = cluster_info
        self.hosts_info = hosts_info

    def get_cluster_id(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info[self.CLUSTER_ID]

    def get_clustername(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None
        return self.cluster_info[self.CLUSTER_NAME]

    def get_os_version(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info[self.OS_VERSION]

    def get_host_id_list(self):
        if not self.hosts_info:
            logging.info("hosts config is None or {}")
            return None

        return self.hosts_info.keys()

    def get_cluster_os_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info[self.OS_CONFIG]

    def get_cluster_package_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return self.cluster_info[self.PK_CONFIG]

    def get_cluster_network_mapping(self):
        package_config = self.get_cluster_package_config()
        if not package_config:
            logging.info("cluster package_config is None or {}.")
            return None

        if self.NETWORK_MAPPING not in package_config:
            return None

        return package_config[self.NETWORK_MAPPING]

    def get_cluster_deploy_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        if self.DEPLOY_CONFIG in self.cluster_info:
            self.cluster_info.setdefault(self.DEPLOY_CONFIG, {})

        return self.cluster_info[self.DEPLOY_CONFIG]

    def get_cluster_roles_mapping(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        if self.ROLES_MAPPING not in self.cluster_info[self.DEPLOY_CONFIG]:
            mapping = self._get_roles_mapping_helper()
            self.cluster_info[self.DEPLOY_CONFIG][self.ROLES_MAPPING] = mapping

        return self.cluster_info[self.DEPLOY_CONFIG][self.ROLES_MAPPING]

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
        if self.FULLNAME  not in host_info:
            hostname = self.get_hostname(host_id)
            clustname = self.get_clustername()
            host_info[self.FULLNAME] = '.'.join((hostname, clustname))

        return host_info[self.FULLNAME]

    def get_host_dns(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        if self.DNS not in host_info:
            fullname = self.get_host_fullname(host_id)
            domain = self.get_host_domain(host_id)
            host_info[self.DNS] = '.'.join((fullname, domain))

        return host_info[self.DNS]

    def get_host_mac_address(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info[self.MAC_ADDR]

    def get_hostname(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info[self.HOSTNAME]

    def get_host_networks(self, host_id):
        host_info = self._get_host_info(host_id)
        if not host_info:
            return None
        
        return host_info[self.NETWORKS]

    def get_host_interfaces(self, host_id):
        interfaces = self.get_host_networks(host_id)
        if not interfaces:
            return None

        nic_names = interfaces.keys()
        return nic_names

    def _get_host_interface_config(self, host_id, interface):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)

        if interface not in host_info[self.INTERFACES]:
           logging.info("Cannot find NIC '%s'", interface)
           return None

        return host_info[self.NETWORKS][self.INTERFACES][interface]

    def get_host_interface_ip(self, host_id, interface):
        if not self._get_host_interface_config(host_id, interface):
            return None

        interface_config = self._get_host_interface_config(host_id, interface)
        return interface_config[self.IP_ADDR]

    def get_host_interface_netmask(self, host_id, interface):
        if not self._get_host_interface_config(host_id, interface):
            return None

        interface_config = self._get_host_interface_config(host_id, interface)
        return interface_config[self.NETMASK]

    def get_host_os_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info[self.OS_CONFIG]

    def get_host_domain(self, host_id):
        os_config = self.get_host_os_config(host_id)
        if not os_config:
            return None

        return os_config[self.OS_CONFIG_GENERAL][self.DOMAIN]

    def get_host_package_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return host_info[self.PK_CONFIG]

    def get_host_roles(self, host_id):
        host_pk_config = self._get_host_info(host_id)
        if not host_pk_config:
            return None

        return host_pk_config[self.ROLES]

    def get_adapter_name(self):
        return self.adapter_info[self.ADAPTER_NAME]

    def get_adapter_roles(self):
        return self.adapter_info[self.ROLES]

    def get_os_installer_settings(self):
        return self.adapter_info[self.OS_INSTALLER][self.INSTALLER_SETTINGS]

    def get_pk_installer_settings(self):
        return self.adapter_info[self.PK_INSTALLER][self.INSTALLER_SETTINGS]

    def get_os_config_metadata(self):
        return self.adapter_info[self.METADATA][self.OS_CONFIG]

    def get_pk_config_meatadata(self):
        return self.adapter_info[self.METADATA][self.PK_CONFIG]

    def _get_roles_mapping_helper(self):
        """The ouput format will be as below, for example:
           {
               "controller": [
                   {
                       "management": {
                           "interface": "eth0",
                           "ip": "192.168.1.10",
                           "netmask": "255.255.255.0"
                       },
                       ...
                   },
                   ...
               ],
               ....
           }
        """
        mapping = {}
        hosts_id_list = self.get_host_id_list()
        network_mapping = self.get_cluster_network_mapping()
        if not network_mapping:
            return None

        for host_id in hosts_id_list:
            temp = {}
            host_roles = self.get_host_roles()
            interfaces = self.get_host_interfaces(host_id)
            for key in network_mapping:
                nic = network_mapping[key]["interface"]
                if nic in interfaces:
                    temp[key]["interface"] = nic
                    temp[key]["ip"] = self.get_host_interface_ip(host_id, nic)
                    temp[key]["netmask"] = self.get_host_interface_netmask(
                                           host_id, nic)
            for role in host_roles:
                if role not in mapping:
                    mapping.setdefault(role, [])
                mapping[role].append(temp)
        
        return mapping       
