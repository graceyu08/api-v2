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

        adapter_info = _get_adapter_info(cluster_id)
        cluster_info = _get_cluster_info(cluster_id)
        hosts_info = _get_hosts_info(hosts_id_list)

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

        adapter_info = _get_adapter_info(cluster_id)
        cluster_info = _get_cluster_info(cluster_id, redeploy=True)
        hosts_info = _get_hosts_info(hosts_id_list, redeploy=True)

        deploy_manager = DeployManager(adapter_info, cluster_info, hosts_info)
        deploy_manager.prepare_for_deploy()
        deploy_manager.redeploy()

def _get_adapter_info(cluster_id):
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

def _get_cluster_info(cluster_id, redeploy=False):
    """Get cluster information."""
    pass

def _get_hosts_info(self, hosts_id_list, redeploy=False):
    """Get hosts information."""
    pass
