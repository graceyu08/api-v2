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

"""Module to deploy a given cluster
"""
import logging

from compass.actions import util
from compass.db import db_api
from compass.deployment.deploy_manager import DeployManager
from compass.deployment.deploy_manager import PowerManager


def deploy(cluster_id, hosts_id_list):
    """Deploy clusters.

    :param cluster_hosts: clusters and hosts in each cluster to deploy.
    :type cluster_hosts: dict of int or str to list of int or str

    .. note::
        The function should be called out of database session.
    """
    with util.lock('serialized_action') as lock:
        if not lock:
            raise Exception('failed to acquire lock to deploy')

        adapter_info = __get_adapter_info(cluster_id)
        cluster_info = __get_cluster_info(cluster_id)
        hosts_info = __get_hosts_details(hosts_id_list)

        deploy_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        deploy_manager.prepare_for_deploy()
        deploy_manager.deploy()


def redeploy(cluster_id, hosts_id_list):
    """Deploy clusters.

    :param cluster_hosts: clusters and hosts in each cluster to deploy.
    :type cluster_hosts: dict of int or str to list of int or str
    """
    with util.lock('serialized_action') as lock:
        if not lock:
            raise Exception('failed to acquire lock to deploy')

        adapter_info = __get_adapter_info(cluster_id)
        cluster_info = __get_cluster_info(cluster_id)
        hosts_info = __get_hosts_details(cluster_id, hosts_id_list)

        deploy_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        deploy_manager.prepare_for_deploy()
        deploy_manager.redeploy()


def poweron(host_id):
    """Power on a list of hosts."""
    with util.lock('serialized_action') as lock:
        if not lock:
            raise Exception('failed to acquire lock to deploy')

        ipmi_info = __get_single_host_ipmi(host_id)
        host_baseinfo = __get_hosts_baseinfo()
        origin_cluster_id = 
        adapter_info = __get_adapter_info(cluster_id)
        hosts_ipmi_info = __get_hosts_ipmi_info(hosts_id_list)


def __get_adapter_info(cluster_id):
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

def __get_cluster_info(cluster_id):
    """Get cluster information.Return a dictionary as below,
       {
           "cluster": {
               "cluster_id": 1,
               "os_version": "CentOS-6.5-x86_64",
               "cluster_name": "cluster_01",
               "os_config": {..},
               "package_config": {...},
               "deploy_os_config": {},
               "deploy_package_config": {}
           }
       }
    """
    pass

def __get_single_host_ipmi(host_id):
    pass


def __get_hosts_baseinfo(cluster_id, hosts_id_list):
    pass

def __get_hosts_details(cluster_id, hosts_id_list):
    """Get hosts information. Return a dictionary as below,
       {
           "hosts": {
               1(host_id): {
                    "host_id": 1,
                    "reinstall_os": True,
                    "os_version": "CentOS-6.5-x86_64",
                    "mac_address": "xxx",
                    "hostname": "xxx",
                    },
                    "networks": {
                         "interfaces": {
                             "eth0": {
                                 "ip": "192.168.1.1",
                                 "netmask": "255.255.255.0",
                                 "is_mgmt": True,
                                 "is_promiscuous": False,
                                 "subnet": "192.168.1.0/24"
                             },
                             "eth1": {...}
                         }
                    },
                    "os_config": {},
                    "package_config": {},
                    "deploy_os_config": {},
                    "deploy_package_config": {}
               },
               2: {...},
               ....
           }
       }
    """
    hosts_info = {}
    for host_id in hosts_id_list:
        host_info = db_api.get_host(host_id)
        hosts_info[host_id] = host_info

    return hosts_info


def __get_hosts_ipmi_info(hosts_id_list):
    """Get IPMI info for each host. The return format will be:
       {
           "hosts": {
               1: {
                   "hostname": "xxx",
                   "ipmi_credentials": {
                        "ip": "xxx",
                        "username": "xxx",
                        "password": "xxx"
                   }
               },
               2: {...},
               ....
           } 
       }
    """
    pass
