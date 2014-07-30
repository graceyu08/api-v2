# Copyright 2014 Huawei Technologies Co. Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Grace Yu (grace.yu@huawei.com)"


"""All keywords variables in deployment are defined in this module."""


#General keywords
CLUSTER = 'cluster'
HOST = 'host'
ID = 'id'
NAME = 'name'
PASSWORD = 'password'
USERNAME = 'username'


#Adapter info related keywords
DIST_SYS_NAME = 'distributed_system_name'
INSTALLER_SETTINGS = 'settings'
METADATA = 'metadata'
PK_INSTALLER = 'pk_installer'
OS_INSTALLER = 'os_installer'
SUPPORT_OSES = 'supported_oses'


#Cluster info related keywords
ADAPTER_ID = 'adapter_id'
OS_VERSION = 'os_version'


#Host info related keywords
DNS = 'dns'
DOMAIN = 'domain'
HOST_ID = 'host_id'
HOSTNAME = 'hostname'
IP_ADDR = 'ip'
IPMI = 'ipmi'
IPMI_CREDS = 'ipmi_credentials'
MAC_ADDR = 'mac'
MGMT_NIC_FLAG = 'is_mgmt'
NETMASK = 'netmask'
NETWORKS = 'networks'
NIC = 'interface'
ORIGIN_CLUSTER_ID = 'origin_cluster_id'
PROMISCUOUS_FLAG = 'is_promiscuous'
REINSTALL_OS_FLAG = 'reinstall_os'
SUBNET = 'subnet'


#Cluster/host config related keywords
DEPLOY_OS_CONFIG = 'deploy_os_config'
DEPLOY_PK_CONFIG = 'deploy_package_config'
NETWORK_MAPPING = 'network_mapping'
PK_CONFIG = 'package_config'
OS_CONFIG = 'os_config'
OS_CONFIG_GENERAL = 'general'
ROLES = 'roles'
ROLES_MAPPING = 'roles_mapping'
