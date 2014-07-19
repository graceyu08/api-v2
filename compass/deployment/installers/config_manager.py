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
from copy import deepcopy
from compass.utils import util
import logging


class BaseConfigManager(object):
    CLUSTER_ID = 'cluster_id'
    OS_VERSION = 'os_version'
    CLUSTER_NAME = 'cluster_name'
    DEPLOY_OS_CONFIG = 'deploy_os_config'
    DEPLOY_PK_CONFIG = 'deploy_package_config'
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
    NIC = 'interface'
    IP_ADDR = 'ip'
    NETMASK = 'netmask'
    DOMAIN = 'domain'
    SUBNET = 'subnet'
    PROMISCUOUS_FLAG = 'is_promiscuous'
    MGMT_FLAG = 'is_mgmt'
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

    def get_cluster_baseinfo(self):
        """Get cluster base information, including cluster_id, os_version,
           and cluster_name.
        """
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None
        base_info = {}
        base_info[self.CLUSTER_ID] = self.cluster_info[self.CLUSTER_ID]
        base_info[self.CLUSTER_NAME] = self.cluster_info[self.CLUSTER_NAME]
        base_info[self.OS_VERSION] = self.cluster_info[self.OS_VERSION]
        return base_info

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

        return deepcopy(self.cluster_info[self.OS_CONFIG])

    def get_cluster_package_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        return deepcopy(self.cluster_info[self.PK_CONFIG])

    def get_cluster_network_mapping(self):
        package_config = self.get_cluster_package_config()
        if not package_config:
            logging.info("cluster package_config is None or {}.")
            return None

        if self.NETWORK_MAPPING not in package_config:
            return None

        return deepcopy(package_config[self.NETWORK_MAPPING])

    def get_cluster_deploy_os_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        if self.DEPLOY_OS_CONFIG not in self.cluster_info:
            self.cluster_info[self.DEPLOY_OS_CONFIG] = {}

        return self.cluster_info[self.DEPLOY_OS_CONFIG]

    def get_cluster_deploy_package_config(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        if self.DEPLOY_PK_CONFIG not in self.cluster_info:
            self.cluster_info[self.DEPLOY_PK_CONFIG] = {}

        return self.cluster_info[self.DEPLOY_PK_CONFIG]

    def set_cluster_deploy_os_config(self, deploy_os_config):
        if deploy_os_config is None:
            return

        config = self.get_cluster_deploy_os_config()
        util.merge_dict(config, deploy_os_config)

    def set_cluster_deploy_package_config(self, deploy_pk_config):
        if deploy_pk_config is None:
            return

        config = self.get_cluster_deploy_package_config()
        util.merge_dict(config, deploy_pk_config)

    def get_cluster_roles_mapping(self):
        if not self.cluster_info:
            logging.info("cluster config is None or {}")
            return None

        deploy_config = self.get_cluster_deploy_package_config()

        if self.ROLES_MAPPING not in deploy_config:
            mapping = self._get_cluster_roles_mapping_helper()
            deploy_config[self.ROLES_MAPPING] = mapping
        else:
            mapping = deploy_config[self.ROLES_MAPPING]

        return mapping

    def _get_host_info(self, host_id):
        if not self.hosts_info:
            logging.info("hosts config is None or {}")
            return None

        if host_id not in self.hosts_info:
            logging.info("Cannot find host, ID is '%s'", host_id)
            return None

        return self.hosts_info[host_id]

    def get_host_baseinfo(self, host_id):
        """Get host base information."""
        host_info = self._get_host_info(host_id)
        if not host_info:
            return None

        attr_names = [self.OS_INSTALLED_FLAG, self.REINSTALL_OS_FLAG,
                      self.OS_VERSION, self.MAC_ADDR, self.HOSTNAME,
                      self.NETWORKS]
        base_info = {}
        for attr in attr_names:
            temp = host_info[attr]
            if isinstance(temp, dict) or isinstance(temp, list):
                base_info[attr] = deepcopy(temp)
            else:
                base_info[attr] = temp

        base_info[self.HOST_ID] = host_id
        base_info[self.FULLNAME] = self.get_host_fullname(host_id)
        base_info[self.DNS] = self.get_host_dns(host_id)

        return base_info

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

        return deepcopy(host_info[self.NETWORKS])

    def get_host_interfaces(self, host_id):
        networks = self.get_host_networks(host_id)
        if not networks:
            return None

        nic_names = networks[self.INTERFACES].keys()
        return nic_names

    def get_host_interface_config(self, host_id, interface):
        networks = self.get_host_networks(host_id)
        if not networks:
            return None

        interfaces = networks[self.INTERFACES]
        if interface not in interfaces:
           logging.info("Cannot find NIC '%s'", interface)
           return None

        return deepcopy(interfaces[interface])

    def get_host_interface_ip(self, host_id, interface):
        if not self._get_host_interface_config(host_id, interface):
            return None

        interface_config = self.get_host_interface_config(host_id, interface)
        return interface_config[self.IP_ADDR]

    def get_host_interface_netmask(self, host_id, interface):
        if not self.get_host_interface_config(host_id, interface):
            return None

        interface_config = self.get_host_interface_config(host_id, interface)
        return interface_config[self.NETMASK]

    def get_host_interface_subnet(self, host_id, interface):
        nic_config = self.get_host_interface_config(host_id, interface)
        if not nic_config:
            return None

        return nic_config[self.SUBNET]

    def is_interface_promiscuous(self, host_id, interface):
        nic_config = self.get_host_interface_config(host_id, interface)
        if not nic_config:
            raise Exception("Cannot find interface '%s'", interface)

        return nic_config[self.PROMISCUOUS_FLAG]

    def is_interface_mgmt(self, host_id, interface):
        nic_config = self.get_host_interface_config(host_id, interface)
        if not nic_config:
            raise Exception("Cannot find interface '%s'", interface)

        return nic_config[self.MGMT_FLAG]

    def get_host_os_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return deepcopy(host_info[self.OS_CONFIG])

    def get_host_domain(self, host_id):
        os_config = self.get_host_os_config(host_id)
        if not os_config:
            return None

        return os_config[self.OS_CONFIG_GENERAL][self.DOMAIN]

    def get_host_network_mapping(self, host_id):
        package_config = self.get_host_package_config(host_id)
        if self.NETWORK_MAPPING not in package_config:
            network_mapping  = self.get_cluster_network_mapping()
        else:
            network_mapping = package_config[self.NETWORK_MAPPING]

        return network_mapping

    def get_host_package_config(self, host_id):
        if not self._get_host_info(host_id):
            return None

        host_info = self._get_host_info(host_id)
        return deepcopy(host_info[self.PK_CONFIG])

    def get_host_deploy_os_config(self, host_id):
        host_info = self._get_host_info(host_id)
        if not host_info:
            return None

        if self.DEPLOY_OS_CONFIG not in host_info:
            host_info[self.DEPLOY_OS_CONFIG] = {}

        return host_info[self.DEPLOY_OS_CONFIG]

    def set_host_deploy_os_config(self, host_id, deploy_config):
        if deploy_config is None:
            return

        config = self.get_host_deploy_os_config(host_id)
        util.merge_dict(config, deploy_config)

    def get_host_deploy_package_config(self, host_id):
        host_info = self._get_host_info(host_id)
        if not host_info:
            return None

        if self.DEPLOY_PK_CONFIG not in host_info:
            host_info[self.DEPLOY_PK_CONFIG] = {}

        return host_info[self.DEPLOY_PK_CONFIG]

    def set_host_deploy_package_config(self, host_id, deploy_config):
        if deploy_config is None:
            return
        config = self.get_host_deploy_package_config(host_id)
        util.merge_dict(config, deploy_config)

    def get_host_roles(self, host_id):
        host_pk_config = self.get_host_package_config(host_id)
        if not host_pk_config:
            return None

        return host_pk_config[self.ROLES]

    def get_host_roles_mapping(self, host_id):
        roles_mapping = {}
        deployed_pk_config = self.get_host_deploy_package_config(host_id)
        if self.ROLES_MAPPING not in deployed_pk_config:
            roles_mapping = self._get_host_roles_mapping_helper(host_id)
        else:
            roles_mapping = deployed_pk_config[self.ROLES_MAPPING]

        return roles_mapping

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

    def _get_cluster_roles_mapping_helper(self):
        """The ouput format will be as below, for example:
           {
               "controller": {
                   "management": {
                       "interface": "eth0",
                       "ip": "192.168.1.10",
                       "netmask": "255.255.255.0",
                       "subnet": "192.168.1.0/24",
                       "is_mgmt": True,
                       "is_promiscuous": False
                   },
                   ...
               },
                   ...
           }
        """
        mapping = {}
        hosts_id_list = self.get_host_id_list()
        network_mapping = self.get_cluster_network_mapping()
        if not network_mapping:
            return None

        for host_id in hosts_id_list:
            roles_mapping = self.get_host_roles_mapping(host_id)
            for role in roles_mapping:
                if role not in mapping:
                    mapping[role] = roles_mapping[role]

        return mapping

    def _get_host_roles_mapping_helper(self, host_id):
        """The format will be the same as cluster roles mapping."""
        mapping = {}
        network_mapping = self.get_host_network_mapping(host_id)
        if not network_mapping:
            return None

        roles = self.get_host_roles(host_id)
        interfaces = self.get_host_interfaces(host_id)
        temp = {}
        for key in network_mapping:
            nic = network_mapping[key][self.NIC]
            if nic in interfaces:
                temp[key] = self.get_host_interface_config(host_id, nic)
                temp[key][self.NIC] = nic

        for role in roles:
            role = role.replace("-", "_")
            mapping[role] = temp
        return mapping
