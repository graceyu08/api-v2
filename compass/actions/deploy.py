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
from compass.db import api as db_api
from compass.deployment.deploy_manager import DeployManager
from compass.deployment.utils import constants as const


def deploy(cluster_id, hosts_id_list, user=None):
    """Deploy clusters.

    :param cluster_hosts: clusters and hosts in each cluster to deploy.
    :type cluster_hosts: dict of int or str to list of int or str

    .. note::
        The function should be called out of database session.
    """
    with util.lock('serialized_action') as lock:
        if not lock:
            raise Exception('failed to acquire lock to deploy')

        cluster_info = __get_cluster_info(cluster_id, user)
        adapter_id = cluster_info[const.ADAPTER_ID]

        adapter_info = __get_adapter_info(adapter_id, cluster_id, user)
        hosts_info = __get_hosts_info(hosts_id_list, user)

        deploy_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        deploy_manager.prepare_for_deploy()
        deploy_manager.deploy()


def redeploy(cluster_id, hosts_id_list, user=None):
    """Deploy clusters.

    :param cluster_hosts: clusters and hosts in each cluster to deploy.
    :type cluster_hosts: dict of int or str to list of int or str
    """
    with util.lock('serialized_action') as lock:
        if not lock:
            raise Exception('failed to acquire lock to deploy')

        cluster_info = __get_cluster_info(cluster_id)
        adapter_id = cluster_info[const.ADAPTER_ID] 

        adapter_info = __get_adapter_info(adapter_id, cluster_id, user)
        hosts_info = __get_hosts_info(cluster_id, hosts_id_list, user)

        deploy_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        deploy_manager.prepare_for_deploy()
        deploy_manager.redeploy()


def poweron(host_id):
    """Power on a list of hosts."""
    pass

def poweroff(host_id):
    pass

def reset(host_id):
    pass


def __get_adapter_info(adapter_id, cluster_id, user):
        """Get adapter information. Return a dictionary as below,
           {
              "id": 1,
              "name": "xxx",
              "roles": ['xxx', 'yyy', ...],
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
              },
              ...
           }
           To view a complete output, please refer to backend doc.
        """
        adapter_info = db_api.adapter_holder.get_adapter(user, adapter_id)
        metadata = db_api.cluster.get_cluster_metadata(user, cluster_id)
        adapter_info.update(metadata)

        roles_info = adapter_info[const.ROLES]
        roles_list = [role[const.NAME] for role in roles_info]
        adapter_info[const.ROLES] = roles_list

        return adapter_info

def __get_cluster_info(cluster_id, user):
    """Get cluster information.Return a dictionary as below,
       {
           "cluster": {
               "id": 1,
               "adapter_id": 1,
               "os_version": "CentOS-6.5-x86_64",
               "name": "cluster_01",
               "os_config": {..},
               "package_config": {...},
               "deploy_os_config": {},
               "deploy_package_config": {},
               "owner": "xxx"
           }
       }
    """
    cluster_info = db_api.cluster.get_cluster(user, cluster_id)
    cluster_config = db_api.cluster.get_cluster_config(user, cluster_id)
    cluster_info.update(cluster_config)

    deploy_config = db_api.cluster.get_cluster_deploy_config(user, cluster_id)
    cluster_info.update(deploy_config)

    return cluster_info


def __get_hosts_info(cluster_id, hosts_id_list, user):
    """Get hosts information. Return a dictionary as below,
       {
           "hosts": {
               1($clusterhost_id/host_id): {
                    "reinstall_os": True,
                    "mac": "xxx",
                    "name": "xxx",
                    },
                    "networks": {
                        "eth0": {
                            "ip": "192.168.1.1",
                            "netmask": "255.255.255.0",
                            "is_mgmt": True,
                            "is_promiscuous": False,
                            "subnet": "192.168.1.0/24"
                        },
                        "eth1": {...}
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
    for clusterhost_id in hosts_id_list:
        info = db_api.cluster.get_cluster_host(user, cluster_id,
                                               clusterhost_id)
        host_id = info[const.HOST_ID]
        temp = db_api.host.get_host(user, host_id)
        info.update(temp)

        networks = info[const.NETWORKS]
        if isinstance(networks, list):
            networks_dict = {}
            for entity in networks:
                nic_info = {}
                nic_info = {
                    entity[const.NIC]: {
                        const.IP_ADDR: entity[const.IP_ADDR],
                        const.NETMASK: entity[const.NETMASK],
                        const.MGMT_NIC_FLAG: entity[const.MGMT_NIC_FLAG],
                        const.PROMISCUOUS_FLAG: entity[const.PROMISCUOUS_FLAG],
                        const.SUBNET: entity[const.SUBNET]
                    }
                }
                networks_dict.update(nic_info)

            info[const.NETWORKS] = networks_dict

        hosts_info[host_id] = info

    return hosts_info
